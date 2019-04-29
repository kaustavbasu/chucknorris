# -*- coding: utf-8 -*-

#    File name: jsonParser.py
#    Author: Kaustav Basu
#    Date created: 01/22/2019
#    Date last modified: 01/22/2019
#    Python Version: 2.7.10

import json
import pandas as pd

youngList = []
midList = []
oldList = []

with open('sinclair_ksnv_march_FB_videoposts_insights.json') as f:
    demoData = json.load(f)

with open('sinclair_ksnv_march_FB_videoposts_info.json') as f:
    commData = json.load(f)

parameter = 'engs'

for c in demoData:
    record = demoData[c][0]['data']
    for i in range(len(record)):
        title = record[i]['title']
        if title == 'Lifetime Video View Time (in MS) by Top Audience' and parameter == 'demo':
            demos = record[i]['values'][0]['value']
            young = 0
            mid = 0
            old = 0
            for d in demos:
                if d == 'U.65+' or d == 'F.65+' or d == 'M.65+':
                    old = old + demos[d]
                elif d == 'M.25-34' or d == 'F.25-34' or d == 'U.25-34' or d == 'M.18-24' or d == 'F.18-24' or d == 'U.18-24' or d == 'M.13-17' or d == 'F.13-17' or d == 'U.13-17':
                    young = young + demos[d]
                else:
                    mid = mid + demos[d]
            print(c+'\t'+str(young)+'\t'+str(mid)+'\t'+str(old))
        if title == 'Lifetime Unique Video Views' and parameter == 'views':
            views = record[i]['values'][0]['value']
            print(c+'\t'+str(views))
        if title == 'Lifetime Total post Reactions by Type.' and parameter == 'engs':
            engs = record[i]['values'][0]['value']
            totalEngs = 0
            for e in engs:
                totalEngs = totalEngs + engs[e]
            print(c+'\t'+str(totalEngs))

if parameter == 'text':
    for i in range(len(commData)):
        id = commData[i]['id']
        comments = 0
        if 'comments' in commData[i]:
            comments = len(commData[i]['comments']['data'])
        title = ''
        if 'title' in commData[i]['attachments']['data'][0]:
            title = commData[i]['attachments']['data'][0]['title']
        print(id+'\t'+str(comments)+'\t'+title)
