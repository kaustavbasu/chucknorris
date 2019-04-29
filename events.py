# -*- coding: utf-8 -*-

#    File name: events.py
#    Author: Kaustav Basu
#    Date created: 03/22/2019
#    Date last modified: 03/22/2019
#    Python Version: 2.7.10

from yelpapi import YelpAPI
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from datetime import timedelta
from prettytable import PrettyTable
import json
import sys
import dateutil.parser as dp


def getVideoData(response, client):
    videoIds = ''
    numResults = len(response['items'])
    for x in range(numResults):
        if 'id' in response['items'][x]:
            videoIds = videoIds+response['items'][x]['id']['videoId']+','
    videoIds = videoIds[0:len(videoIds)-1]
    response = ''
    if numResults > 0:
        response = videos_list_multiple_ids(client,
              part='snippet,contentDetails,statistics',
              id=videoIds)
    return response

def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.iteritems():
          if value:
            good_kwargs[key] = value
    return good_kwargs

def search_list_by_keyword(client, **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.search().list(
    **kwargs
    ).execute()
    return response

def videos_list_multiple_ids(client, **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.videos().list(
    **kwargs
    ).execute()
    return response

def getEventsFromYelp(location):
    eventsList = []
    startTime = dp.parse((datetime.now() + timedelta(days=7)).isoformat()).strftime('%s')
    yelpApi = YelpAPI('')
    response = yelpApi.event_search_query(location=location, sort_by='desc', limit=50, sort_on='popularity', start_date=startTime)
    events = response['events']
    for i in range(len(events)):
        name = events[i]['name']
        attendingCount = events[i]['attending_count']
        interestedCount = events[i]['interested_count']
        cost = events[i]['cost']
        zip = events[i]['location']['zip_code']
        category = events[i]['category']
        time = events[i]['time_start']
        event = [name, attendingCount, interestedCount, cost, zip, category, time]
        eventsList.append(event)
    return eventsList

def crawlEventOnYoutube(eventName, location):
    videoStats = []
    query = eventName+' '+location
    googleApiKey = ''
    client = build('youtube', 'v3', developerKey = googleApiKey)
    response = search_list_by_keyword(client, part='snippet', maxResults=10, q=query,
        order='date', type='video')
    videoData = getVideoData(response, client)
    numResults = videoData['pageInfo']['totalResults'] if 'pageInfo' in videoData else 0
    totalVideoViews = 0
    totalVideoEngagements = 0
    vidCount = 0
    for i in range(numResults):
        videoTitle = videoData['items'][i]['snippet']['title']
        videoDescription = videoData['items'][i]['snippet']['description']
        videoViews = videoData['items'][i]['statistics']['viewCount'] if 'viewCount' in videoData['items'][i]['statistics'] else 0
        videoLikes = videoData['items'][i]['statistics']['likeCount'] if 'likeCount' in videoData['items'][i]['statistics'] else 0
        videoDislikes = videoData['items'][i]['statistics']['dislikeCount'] if 'dislikeCount' in videoData['items'][i]['statistics'] else 0
        videoFavorites = videoData['items'][i]['statistics']['favoriteCount'] if 'favoriteCount' in videoData['items'][i]['statistics'] else 0
        videoComments = videoData['items'][i]['statistics']['commentCount'] if 'commentCount' in videoData['items'][i]['statistics'] else 0
        if eventName in videoTitle or eventName in videoDescription:
            totalVideoViews = totalVideoViews + int(videoViews)
            totalVideoEngagements = totalVideoEngagements + int(videoLikes) + int(videoDislikes) + int(videoFavorites) + int(videoComments)
            vidCount = vidCount + 1
    videoStats = [totalVideoViews, vidCount, totalVideoEngagements]
    return videoStats

if __name__ == '__main__':
    location = sys.argv[1]
    eventsList = getEventsFromYelp(location)
    t = PrettyTable(['Name', 'Zip Code', 'Category', 'Views', 'Engagements', '# Videos'])
    for i in range(len(eventsList)):
        videoData = crawlEventOnYoutube(eventsList[i][0], location)
        t.add_row([eventsList[i][0], eventsList[i][4], eventsList[i][5], videoData[0], videoData[2], videoData[1]])
    print(t)
