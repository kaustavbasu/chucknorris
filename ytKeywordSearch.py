# -*- coding: utf-8 -*-

#    File name: ytKeywordSearch.py
#    Author: Kaustav Basu
#    Date created: 01/07/2019
#    Date last modified: 01/07/2019
#    Python Version: 2.7.10

import sys
import os
import gender_guesser.detector as gender
import pandas as pd
import progressbar
import xlrd
from time import sleep
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from textblob import TextBlob
from agefromname import AgeFromName
#from ethnicolr import census_ln, pred_census_ln


# API key for YouTube
API_KEY = 'AIzaSyA_z7F9Cb82L90d7MobNYR17WSjcpk71jk'
# Array to hold all vidoes returned by the API
VIDEOS = []

# Create a list of video ids and get stats for each video
def get_video_data(response):
  videoIds = ''
  numResults = len(response['items'])
  for x in range(numResults):
      if 'id' in response['items'][x]:
          videoIds = videoIds+response['items'][x]['id']['videoId']+','
  videoIds = videoIds[0:len(videoIds)-1]
  response = ''
  if numResults > 0:
      response = videos_list_multiple_ids(service,
              part='snippet,contentDetails,statistics',
              id=videoIds)
  return response

# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
  good_kwargs = {}
  if kwargs is not None:
    for key, value in kwargs.iteritems():
      if value:
        good_kwargs[key] = value
  return good_kwargs

# Take keywords and returns videos
def search_list_by_keyword(client, **kwargs):
  kwargs = remove_empty_kwargs(**kwargs)
  response = client.search().list(
    **kwargs
  ).execute()
  return response

# Take video ids and returns video info and stats
def videos_list_multiple_ids(client, **kwargs):
  kwargs = remove_empty_kwargs(**kwargs)
  response = client.videos().list(
    **kwargs
  ).execute()
  return response

# Take channel ids and returns channel info and stats
def channels_list_by_id(client, **kwargs):
  d = gender.Detector(case_sensitive=False)
  kwargs = remove_empty_kwargs(**kwargs)
  response = client.channels().list(
    **kwargs
  ).execute()
  channelTitle = 'No Title'
  channelSubscribers = 0
  if len(response['items']) > 0:
      channelTitle = response['items'][0]['snippet']['title']
      channelSubscribers = response['items'][0]['statistics']['subscriberCount']
  firstName = channelTitle.split(' ', 1)[0]
  if firstName == 'Dr.' or firstName == 'The':
      firstName = channelTitle.split(' ')[1]
  lastName = channelTitle.split(' ')[-1]
  channelOwnerGender = d.get_gender(firstName)
  channelOwner = [channelTitle, channelOwnerGender, channelSubscribers]
  return channelOwner

def agg_results(keywords, response, client):
     numResults = response['pageInfo']['totalResults']
     for i in range(numResults):
         videoTitle = response['items'][i]['snippet']['title']
         videoDescription = response['items'][i]['snippet']['description']
         videoId = response['items'][i]['id']
         videoPublished = response['items'][i]['snippet']['publishedAt']
         channelId = response['items'][i]['snippet']['channelId']
         channelOwner = channels_list_by_id(client,
               part='snippet,contentDetails,statistics',
               id=channelId)
         channelTitle = channelOwner[0]
         channelOwnerGender = channelOwner[1]
         channelSubscribers = channelOwner[2]
         videoViews = 0
         if 'viewCount' in response['items'][i]['statistics']:
             videoViews = response['items'][i]['statistics']['viewCount']
         videoLikes = 0
         if 'likeCount' in response['items'][i]['statistics']:
             videoLikes = response['items'][i]['statistics']['likeCount']
         videoDislikes = 0
         if 'dislikeCount' in response['items'][i]['statistics']:
             videoDislikes = response['items'][i]['statistics']['dislikeCount']
         videoFavorites = 0
         if 'favoriteCount' in response['items'][i]['statistics']:
             videoFavorites = response['items'][i]['statistics']['favoriteCount']
         videoComments = 0
         if 'commentCount' in response['items'][i]['statistics']:
             videoComments = response['items'][i]['statistics']['commentCount']
         text = TextBlob(videoTitle)
         phrases = ",".join(text.noun_phrases)
         video = [keywords, videoTitle, videoId, videoPublished, channelId, channelTitle,
                  channelOwnerGender, channelSubscribers, videoViews, videoLikes,
                  videoDislikes, videoFavorites, videoComments, phrases, videoDescription]
         VIDEOS.append(video)

def keywordSearch(keywords, orderBy, client):
     # How many results to return in each page
     resPerPage = 50
     # Should more than one page of results be returned
     paginate = False
     # How many total pages to return
     maxPages = 10
     # Counter for pages returned
     pageCounter = 1
     # Instantiate progress bar and start it
     bar = progressbar.ProgressBar(maxval=maxPages, \
     widgets=[progressbar.Bar('=', 'Progress [', ']'), ' ', progressbar.Percentage()], term_width=100)
     bar.start()
     # Call API and return first page of results
     response = search_list_by_keyword(service,
     	part='snippet',
     	maxResults=resPerPage,
     	q=keywords,
        order=orderBy,
        relevanceLanguage='en',
     	type='video')
     # Get token for next page
     nextPageToken = ''
     if 'nextPageToken' in response:
         nextPageToken = response['nextPageToken']
     numResults = response['pageInfo']['resultsPerPage']
     # Get performance data for each video returned
     videoData = get_video_data(response)
     # Aggregate results
     agg_results(keywords, videoData, service)
     # Update progress bar
     bar.update(pageCounter)
     # If returning more than one page of results and if maxPages has not been returned
     while nextPageToken != None and pageCounter < maxPages and paginate and numResults >= resPerPage:
         pageCounter = pageCounter + 1
         response = search_list_by_keyword(service,
         	part='snippet',
         	maxResults=resPerPage,
         	q=keywords,
            order=orderBy,
            relevanceLanguage='en',
            pageToken=nextPageToken,
         	type='video')
         nextPageToken = response['nextPageToken']
         if len(response['items']) == 0:
             numResults = 0
         else:
             numResults = response['pageInfo']['resultsPerPage']
             videoData = get_video_data(response)
             agg_results(keywords, videoData, service)
         bar.update(pageCounter)
     # End progress bar
     bar.finish()
     # Print results
     print('Total results: '+str(response['pageInfo']['totalResults']))
     printResults(keywords)

def fileSearch(keywords, orderBy, client):
     # How many results to return in each page
     resPerPage = 50
     # Should more than one page of results be returned
     paginate = False
     # How many total pages to return
     maxPages = 1
     # Counter for pages returned
     pageCounter = 1
     # Location of input file
     loc = keywords
     wb = xlrd.open_workbook(loc)
     sheet = wb.sheet_by_index(0)
     # Instantiate progress bar and start it
     bar = progressbar.ProgressBar(maxval=sheet.nrows, \
     widgets=[progressbar.Bar('=', 'Progress [', ']'), ' ', progressbar.Percentage()], term_width=100)
     bar.start()
     for x in range(sheet.nrows):
         # Call API and return first page of results
         response = search_list_by_keyword(service,
         	part='snippet',
         	maxResults=resPerPage,
         	q=sheet.cell_value(x, 0),
            order=orderBy,
            relevanceLanguage='en',
         	type='video')
         # Get token for next page
         #nextPageToken = response['nextPageToken']
         numResults = response['pageInfo']['resultsPerPage']
         # Get performance data for each video returned
         videoData = get_video_data(response)
         # Aggregate results
         agg_results(sheet.cell_value(x, 0), videoData, service)
         # Update progress bar
         bar.update(x)
         # If returning more than one page of results and if maxPages has not been returned
         #while nextPageToken != None and pageCounter < maxPages and paginate and numResults >= resPerPage:
             #pageCounter = pageCounter + 1
             #response = search_list_by_keyword(service,
             	#part='snippet',
             	#maxResults=resPerPage,
             	#q=keywords,
                #order=orderBy,
                #relevanceLanguage='en',
                #pageToken=nextPageToken,
             	#type='video')
             #nextPageToken = response['nextPageToken']
             #if len(response['items']) == 0:
                 #numResults = 0
             #else:
                 #numResults = response['pageInfo']['resultsPerPage']
                 #videoData = get_video_data(response)
                 #agg_results(sheet.cell_value(x, 0), videoData, service)
             #bar.update(x)
     # End progress bar
     bar.finish()
     # Print results
     printResults('output')

def printResults(name):
    pd.set_option('display.max_rows', 1000)
    df = pd.DataFrame(VIDEOS, columns=['Keyword','Video','Video ID','Published Date','Channel ID','Channel Name',
                                            'Channel Owner Gender','Subscribers','Views','Likes','Dislikes',
                                            'Favorites','Comments','Keywords','Video Description'])
    if name is 'output':
        df.to_excel('crawl_outputs/output.xlsx', index=False)
        print('Done! Check output.xlsx file for results')
    else:
        df.to_excel('crawl_outputs/'+name+'.xlsx', index=False)
        print('Done! Check "crawl_outputs/'+name+'.xlsx\" file for results')
    print('\n\n')
    script = 'python /Users/kaustavbasu/Desktop/API/crawls/extractKeywords.py \''+name+'\'.xlsx'
    os.system(script)

# Main function
if __name__ == '__main__':
    os.system('clear')
    # Get command line args
    keywords = sys.argv[1]
    orderBy = 'viewCount'
    if len(sys.argv) > 2:
        orderBy = sys.argv[2]
    # Build YouTube API service
    service = build('youtube', 'v3', developerKey = API_KEY)
    if ".xlsx" not in keywords:
        keywordSearch(keywords, orderBy, service)
    else:
        fileSearch(keywords, orderBy, service)
