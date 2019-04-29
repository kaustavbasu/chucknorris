# -*- coding: utf-8 -*-

#    File name: ytNameSearch.py
#    Author: Kaustav Basu
#    Date created: 12/19/2018
#    Date last modified: 12/19/2018
#    Python Version: 2.7.10

import os

import google.oauth2.credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

import json
import xlrd

# API key for YouTube
API_KEY = ''

def get_authenticated_service():
  return build('youtube', 'v3', developerKey = API_KEY)

def print_response(response):
  if len(response['items']) > 0:
      print(response['items'][0]['snippet']['title']+"\t"+response['items'][0]['snippet']['channelId'])

# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
  good_kwargs = {}
  if kwargs is not None:
    for key, value in kwargs.iteritems():
      if value:
        good_kwargs[key] = value
  return good_kwargs

def search_list_by_keyword(client, **kwargs):
  # See full sample for function
  kwargs = remove_empty_kwargs(**kwargs)

  response = client.search().list(
    **kwargs
  ).execute()

  return print_response(response)


if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification. When
  # running in production *do not* leave this option enabled.
  os.system('clear')
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  client = get_authenticated_service()

  loc = ("creators.xlsx")

  wb = xlrd.open_workbook(loc)
  sheet = wb.sheet_by_index(0)

  for x in range(sheet.nrows):
  	search_list_by_keyword(client,
    	part='snippet',
    	maxResults=1,
    	q=sheet.cell_value(x, 0),
    	type='channel')
