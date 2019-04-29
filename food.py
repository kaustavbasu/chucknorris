# -*- coding: utf-8 -*-

#    File name: food.py
#    Author: Kaustav Basu
#    Date created: 03/22/2019
#    Date last modified: 03/22/2019
#    Python Version: 2.7.10

from yelpapi import YelpAPI
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from prettytable import PrettyTable
import json
import sys

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

def getRestaurantsFromYelp(location):
    restaurantsList = []
    yelpApi = YelpAPI('i0_-J0g6lVcvsWv-TtAtdokJd-sooLR3FVVeYZ5Yje6BOenKi9bULEDjJRXq6DI6WywHqyk7evM3ngKS02WyvPo-R4ao1ZQxZCwjTXDJJDVGT8BdNEpOD2ii3NeUXHYx')
    response = yelpApi.search_query(term='restaurant', location=location, sort_by='rating', limit=25, attributes='hot_and_new')
    restaurants = response['businesses']
    for i in range(len(restaurants)):
        name = restaurants[i]['name']
        rating = restaurants[i]['rating']
        reviewCount = restaurants[i]['review_count']
        price = restaurants[i]['price'] if 'price' in restaurants[i] else 'NA'
        zip = restaurants[i]['location']['zip_code']
        categories = restaurants[i]['categories']
        catList = []
        for category in categories:
            catList.append(category['title'])
        restaurant = [name, rating, reviewCount, price, zip, catList]
        restaurantsList.append(restaurant)
    #print(restaurants)
    return restaurantsList

def crawlRestaurantOnYoutube(restaurantName, location):
    videoStats = []
    query = restaurantName+' restaurant '+location
    googleApiKey = 'AIzaSyA_z7F9Cb82L90d7MobNYR17WSjcpk71jk'
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
        if restaurantName in videoTitle or restaurantName in videoDescription:
            totalVideoViews = totalVideoViews + int(videoViews)
            totalVideoEngagements = totalVideoEngagements + int(videoLikes) + int(videoDislikes) + int(videoFavorites) + int(videoComments)
            vidCount = vidCount + 1
    videoStats = [totalVideoViews, vidCount, totalVideoEngagements]
    return videoStats

if __name__ == '__main__':
    location = sys.argv[1]
    restaurantsList = getRestaurantsFromYelp(location)
    t = PrettyTable(['Name', 'Zip Code', 'Categories', 'Views', 'Engagements', '# Videos'])
    for i in range(len(restaurantsList)):
        videoData = crawlRestaurantOnYoutube(restaurantsList[i][0], location)
        t.add_row([restaurantsList[i][0], restaurantsList[i][4], restaurantsList[i][5], videoData[0], videoData[2], videoData[1]])
    print(t)
