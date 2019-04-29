# -*- coding: utf-8 -*-

#    File name: extractKeywords.py
#    Author: Kaustav Basu
#    Date created: 02/07/2019
#    Date last modified: 02/07/2019
#    Python Version: 2.7.10

from textblob import TextBlob
from collections import Counter
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from prettytable import PrettyTable
from prettytable import MSWORD_FRIENDLY
from prettytable import NONE
import xlrd
import enchant
import sys

def removeStopwords(text):
    stopWords = set(stopwords.words('english'))
    newStopWords = ['subscribe','facebook','twitter','instagram','google+','tumblr',
                    'patreon','youtube','channel','http','https','video','twitch','top','subscribe','2019'
                    ,'pinterest','videos','video','trends','watch','today','york']
    stopWords.update(newStopWords)
    words = word_tokenize(text)
    cleanText = ''
    d = enchant.Dict('en_US')
    for w in words:
        if w.lower() not in stopWords and d.check(w):
            cleanText = cleanText + w + ' '
    return cleanText


if __name__ == '__main__':
    # Get command line args
    fileName = sys.argv[1]
    workbookName = 'crawl_outputs/'+fileName
    file = xlrd.open_workbook(workbookName)
    t = PrettyTable(['Topic', 'Count', 'Views', 'Engagements'])
    t.align['Topic'] = 'l'
    t.align['Count'] = 'r'
    t.align['Views'] = 'r'
    t.align['Engagements'] = 'r'
    t.set_style(MSWORD_FRIENDLY)
    t.vrules = NONE
    for i in range(file.nsheets):
        keywords = []
        keywordMetrics = []
        topic = file.sheet_by_index(i).name
        sheet = file.sheet_by_index(i)
        for row in range(1, sheet.nrows):
            text = sheet.cell_value(row,1)
            #text = sheet.cell_value(row,2)
            cleanText = TextBlob(removeStopwords(text))
            videoId = sheet.cell_value(row,2)
            #videoId = sheet.cell_value(row,0)
            views = int(sheet.cell_value(row,8))
            #views = int(sheet.cell_value(row,5))
            #uniqueViews = int(sheet.cell_value(row,6))
            engagements = int(sheet.cell_value(row,9)) + int(sheet.cell_value(row,10)) + int(sheet.cell_value(row,11)) + int(sheet.cell_value(row,12))
            #engagements = int(sheet.cell_value(row,7))
            phrases = cleanText.noun_phrases
            for x in range(len(phrases)):
                #print(phrases[x]+'\t'+str(views)+'\t'+str(engagements))
                keywords.append(phrases[x])
                keywordMetric = [phrases[x], views, engagements]
                #keywordMetric = [phrases[x], views, engagements, uniqueViews]
                keywordMetrics.append(keywordMetric)
        uniqueKeywords = Counter(keywords).most_common(100)
        for x in uniqueKeywords:
            #print(topic+'\t'),
            #print(x[0]+'\t'),
            #print(str(x[1])+'\t'),
            v = 0
            e = 0
            u = 0.00
            for y in range(len(keywordMetrics)):
                if x[0] == keywordMetrics[y][0]:
                    v = v + keywordMetrics[y][1]
                    e = e + keywordMetrics[y][2]
                    #u = u + keywordMetrics[y][3]
            #print(str(v)+'\t'+str(e))
            t.add_row([x[0], x[1], v, e])
        print(t)
