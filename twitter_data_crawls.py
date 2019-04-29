#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 09:57:47 2018
@author: hkaraky
Originally Implemented In Jupyter Ntbks, Transferred into a Spyder Script
"""
import pandas as pd
import tweepy
import re
import os
import inspect
from tweepy import OAuthHandler
from textblob import TextBlob
import simplejson, urllib
import traceback

#USER INPUT
client_handle = "sarahkilroy" #Insert Client's Twitter handle (without @) if pulling followers
keyword = "mclean" #Insert Keyword if Searching for Tweets
task = "Search" #Search or Followers depending on task
path_for_all_files = ""#input path here else th default would be  a folder in Documents with client_handle/keyword as name

cwd = os.getcwd()
folder_scripts = "/".join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))).split("/")[0:-1])
if task == "Followers":
    path_for_all_files = "/".join(cwd.split("/")[0:3]) + "/Documents/" + client_handle
elif task =="Search":
    path_for_all_files = "/".join(cwd.split("/")[0:3]) + "/Documents/" + keyword
if not os.path.exists(path_for_all_files):
    os.makedirs(path_for_all_files)
search_file_to_save_in = path_for_all_files + "/search_geo_crawl.csv"
saved_search_results = path_for_all_files + "/saved_search_results.csv"
followers_file_to_save_in = path_for_all_files + "/followers_geo_crawl.csv"

fail_count = 0 #check for google api key (as long as it's 0 it hasn't maxed out)
#Twitter Key 1
CONSUMER_KEY = 'BIXfLkOtcUYoqZimalXucKoaw'
CONSUMER_SECRET = 'TPcXMnN0hYXO64yxpBD67ckAqCWwMxzNkjTIgtwz5qFuEHRrTC'
ACCESS_TOKEN ="723211678016393219-ZBSX4Gi4Kgw7QJ8KJ72ogBWD1M1GZva"
ACCESS_SECRET = 'jMhNXfk9BdLKx0P04ui5yiEymPFqXS7WGtUDqd1KTLQ42'

#Twitter Key 2
#CONSUMER_KEY = 'lq7V9OIoDLdcmoE82nDnpgqLM'
#CONSUMER_SECRET = '29C8PkSLv5oz0eiJEOZCYn4rP2A3I46lmR7uk2L0FawPDJYYo9'
#ACCESS_TOKEN = '724394494989336576-wCzg28rYOBiqgLLqUr9kifq1eVhdncv'
#ACCESS_SECRET = 'p4xZk0vxNKmT0afsel2Xs8yjcczpEQaKplVoopWll3u3T'

auth = OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True) #Setting up API, wait_on_rate limit will pause the program and wait for the key to reset every 15 min
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
GEOCODE_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

#%% Cell 0 - Functions
#Geocode function using GOOGLE MAPS API, takes in location, returns lat/lon
def geocode(address, **geo_args):
    geo_args.update({
        'address': address
    })
    try:
        str(address)
    except UnicodeEncodeError: # error thrown if address cannot be converted to a string (i.e contains emojis or other symbols)
        return # return nothing

    # store geocoding response as JSON
    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args) + '&key=AIzaSyClJOFv9ie5SrNNvXMd_5C_wdJ8fuGYUEk'
    x = simplejson.load(urllib.urlopen(url))

    # check if given address can be geolocated
    if x['status'] == 'ZERO_RESULTS':
    #or  'results' not in x or len(x['results'])==0:
        return
    else:
        # relevant info extracted from JSON
        lat = x['results'][0]['geometry']['location']['lat']
        lng = x['results'][0]['geometry']['location']['lng']
        coordinates = (lat, lng)
        return coordinates

#Geocode function using MAPQUEST API, takes in location, returns lat/lon coordinates
def mapgeo(address, **geo_args):
    geo_args.update({
        'location': address
    })

    try:
        str(address)
    except UnicodeEncodeError:
        return
    #Additional MapQuest Key: q4W81kDzwntYAyWMJAjEsMEDlb7BnskH
    MAP_URL = "http://www.mapquestapi.com/geocoding/v1/address?key=SfmyZmI5o96AyWtGvqQCEfEPeJoHHgip" + "&inFormat=kvp&outFormat=json&location=" + urllib.urlencode(geo_args) + "&thumbMaps=false"
    x = simplejson.load(urllib.urlopen(MAP_URL))

    for i in x['results'][0]['locations']:
        if i['geocodeQuality'] == 'CITY':
            lat = i['latLng']['lat']
            lng = i['latLng']['lng']
            coordinates = (lat, lng)
            return coordinates
    return

#Function to return a cleaned version of tweet text (removing urls, hastags, etc.)
def clean_tweet(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

#Function to analyze the sentiment of a given text using textblob
def analyze_sentiment(tweet):
    analysis = TextBlob(clean_tweet(tweet))
    #Very Positive
    if analysis.sentiment.polarity > 0.5:
        return 2
    #Postive
    elif analysis.sentiment.polarity > 0:
        return 1
    #Neutral
    elif analysis.sentiment.polarity == 0:
        return 0
    #Negative
    elif analysis.sentiment.polarity > -0.5:
        return -1
    #Very Negative
    else:
        return -2

#%% Cell 1 - Pulling follower information/location to gather audience insights
if task == "Followers":
    fdata = pd.DataFrame(columns = {'Follower_ID', 'Screen_Name', 'Name', 'Description', 'Location'})
    fdata = fdata[['Follower_ID', 'Screen_Name', 'Name', 'Description', 'Location']]

    #Using tweepy.Cursor to search through a user's followers, and pull their id, handle, name, description, and location
    follow_count = 0
    try:
        for user in tweepy.Cursor(api.followers, screen_name=client_handle, count = 1000).items():
            fdata.loc[follow_count] = (user.id, user.screen_name, user.name, user.description, user.location)
            follow_count += 1
    except Exception,e:
        tb = traceback.format_exc()
        print tb
        print("Twitter Handle Invalid, Please Enter a Valid Handle")

    fdata["Coordinates"] = ""
    num_follower_locations = 0 #Number of coordinates pulled
    for i in range(len(fdata)):
        if ',' in fdata.loc[i,"Location"]:
            try:
                fdata.loc[i,"Coordinates"] = geocode(fdata.loc[i,"Location"]) #mapgeo function for MAPQUEST
            except Exception,e:
                tb = traceback.format_exc()
                fail_count+=1
                if fail_count == 1:
                    print tb
                    print("Google Key Maxed Out, Trying Mapquest")
                try:
                    fdata.loc[i,"Coordinates"] = mapgeo(fdata.loc[i,"Location"]) #mapgeo function for MAPQUEST
                except Exception,e:
                    tb = traceback.format_exc()
                    print tb
                    print("Both Mapquest/Google Keys Maxed Out")
                    break
            num_follower_locations += 1
    fdata.to_csv(followers_file_to_save_in, encoding = 'utf8')
#%% Cell 2 - Querying Tweets in Last Week based on Keyword and pulling sentiments/location
if task == "Search":
    search_results = pd.DataFrame(columns = {'Location', 'Tweet Text'})
    search_results = search_results[['Location', 'Tweet Text']]
    search_count = 0

    for tweet in tweepy.Cursor(api.search,q=keyword, count=1000, lang = "en").items():
        if (not tweet.retweeted) and ('RT @' not in tweet.text):
            #print(tweet.user.location, tweet.text)
            search_results.loc[search_count] = (tweet.user.location, tweet.text)
            search_count += 1

    search_results.to_csv(saved_search_results, encoding = 'utf8')
    sdata = pd.read_csv(saved_search_results)
    sdata = sdata.drop(sdata.columns[0], axis=1)
    sdata.columns = ['Location', 'Tweet Text']
    sdata["Coordinates"] = ""
    sdata["Clean Tweet"] = ""
    sdata["Sentiment Score"] = ""
    sdata = pd.DataFrame(sdata[["Location", "Coordinates", "Tweet Text", "Clean Tweet", "Sentiment Score"]])
    sdata = sdata.fillna("")

    for i in range(len(sdata)):
        sdata.iloc[i,3] = clean_tweet(sdata.iloc[i,2])
        sdata.iloc[i,4] = analyze_sentiment(sdata.iloc[i,3])

    sentiment_avg = sdata['Sentiment Score'].mean()
    print('Average Sentiment: ' + str(sentiment_avg))
    print("Sentiment Distribution: " + str(sdata['Sentiment Score'].value_counts())) #Distribution
    num_search_locations = 0 #Number of coordinates pulled

    for i in range(len(sdata)):
        if ',' in sdata.loc[i,"Location"]:
            try:
                sdata.loc[i,"Coordinates"] = geocode(sdata.loc[i,"Location"]) #geocode function for GOOGLE MAPS
            except Exception,e:
                tb = traceback.format_exc()
                fail_count+=1
                if fail_count == 1:
                    print tb
                    print("Google Key Maxed Out, Trying Mapquest")
                try:
                    sdata.loc[i,"Coordinates"] = mapgeo(sdata.loc[i,"Location"]) #mapgeo function for MAPQUEST
                except Exception,e:
                    tb = traceback.format_exc()
                    print tb
                    print("Both Mapquest/Google Keys Maxed Out")
                    break
            num_search_locations += 1
    sdata.to_csv(search_file_to_save_in, encoding = 'utf8')
