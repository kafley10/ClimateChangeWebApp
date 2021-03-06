#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup, Comment
from contextlib import closing
import sys
import re
import json
import io
import os
import ijson
requests.packages.urllib3.disable_warnings()

tweetFileName = ""

# Runs functions in this order: 1) readTweetsFile  2) extractShortURLs 3) extractLongUrls (and webpage text contents)
# To run: python downloadWebpagesFromTweets.py [json file path]


# Input: an array of the texts of each tweet, containing shortened URLs,
# Extracts recognized short urls in the text of each tweet
# Output: a text file [json file]-shorturls.txt with one short url on each line.

# TODO: include file from mohamed that extracts text & title from html reponse

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head']:
        return False
    return True
    
def extractFromHTML(htmlPage):
    soup = BeautifulSoup(htmlPage, "lxml")
    title = ""
    text = ""
    if soup.title:
        if soup.title.string:
            title = soup.title.string
    
    comments = soup.findAll(text=lambda text:isinstance(text,Comment))
    [comment.extract() for comment in comments]
    
    text_nodes = soup.findAll(text=True)
    visible_text = filter(visible, text_nodes)
    text = "\n".join(visible_text)
    return text,title

def extractShortURLsFreqDic(tweetsText):
    shortURLsDic = {}
    regExp = "(?P<url>https?://[a-zA-Z0-9\./-]+)"
    for t in tweetsText:
        #t = t[0]
        url_li = re.findall(regExp, t)  # find all short urls in a single tweet
        while (len(url_li) > 0): 
            surl = url_li.pop()
            
            while surl.endswith("."):
                surl = surl[:-1]
            if surl in shortURLsDic:
                shortURLsDic[surl] += 1
            else:
                shortURLsDic[surl]=1
            #shortURLsList.append()
    return shortURLsDic#shortURLsList
    
# Input: an array of short URLs, makes web requests to try to connect to each short url website.
# Output: a file [json file name]-longurls.txt with a long-url on each tweet
# Output: one file for each valid webpage. i.e. 1.txt for the 2nd valid webpage.
# Only valid URLs (non-404) will be stored in the output text file.
def getOrigLongURLs(shortURLs):
    expandedURLs = {}
        #freqShortURLs = freqShortURLs[:2000]
    i=0
    e=0
    webpages = []
    webpageUrls = []
    for surl,v in shortURLs:
        try:
            with closing(requests.get(surl.strip(), verify=False)) as r:
                #print r.status_code
                if r.status_code == requests.codes.ok:
                    # ignore "webpages" that are too small:
                    if len(r.text) > 5000:
                        # ignore webpages that are actually just tweets:
                        if "twitter.com" not in r.url:
                            ori_url =r.url
                            webpages.append(r.text)
                            webpageUrls.append(r.url + "\n")
                            if ori_url in expandedURLs:
                                expandedURLs[ori_url].append((surl,v))
                            else:
                                expandedURLs[ori_url] = [(surl,v)]
                            i  =i+1
                        else:
                            e = e+1
                    else:
                        e = e+1
                else:
                    e = e+1    
                    #print r.status_code , surl, r.url, r.request.url
                    #expandedURLs.append("")
        except :
            #print sys.exc_info()[0], surl
            #3expandedURLs.append("")
            e = e +1
    print "urls expanded: ", i
    #print "bad Urls: ",e
    return expandedURLs,webpages,webpageUrls,i

# Input: the file location of a tweets JSON file, extracts the text field of each JSON object.
# Output: a local array of the texts of each tweet.
def readTweetsFile(tweetsFile):
	with open(tweetsFile,'r') as f:
		tweets = f.read().decode('utf8', 'ignore')
	
	tweets = json.loads(tweets.replace("\'", '"'))
	#print len(tweets)
	
	texts = {}
	for tweet in tweets:
		if 'id' in tweet:
			if 'text' in tweet:
				texts[tweet['id']] = tweet['text']
			
	#print len(texts)
	return texts.values()

def saveTextToWebpageFiles(webpages,webpageUrls, count):
    #print 'Starting webpages'
    if webpages:
            wpsTxts = []
            wpsTitles = []
            for wp in webpages:
                wpTxt,wpTitle = extractFromHTML(wp)
                wpsTxts.append(wpTxt)
                wpsTitles.append(wpTitle)
            #print 'Saving webpages'
            directory = os.getcwd()
            #print('Current directory: ' + directory)
            directory = directory + '\\' + os.path.splitext(tweetFileName)[0] + '\\'
            #print('Saving in directory: ' + directory)
            #print('Will overwrite if files already exist')
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            for i in range(len(webpages)): # Create text file for each webpage: 0.txt will have the 1st webpage
                    path = directory + '\\' + str(count + i)+'.txt'
                    with open(path,'w') as fw:
                            fw.write(webpageUrls[i].encode('utf8'))
                            fw.write(wpsTitles[i].encode('utf8'))
                            fw.write(wpsTxts[i].encode('utf8'))
            #print 'done'
    else:
            print 'NO webpages'

def saveLongUrls(longURLs):
    if longURLs:
            f = io.open(tweetFileName.split(".")[0] + '-LongURLs.txt','w', encoding='utf-8')
            f.write("\n".join(longURLs.keys()))
            f.close()
            #print len(longURLs),' Long URLs retrieved'
    else:
            print 'No Long URLs'

def processJsonFile(tweetsFileName):
    tweetsTxt = readTweetsFile(tweetsFileName)
    shortURLs = extractShortURLsFreqDic(tweetsTxt)
    f = io.open(tweetFileName.split(".")[0] + '-ShortURLs.txt','w', encoding='utf-8')
    f.write("\n".join(shortURLs.keys()))
    f.close()
    #print len(shortURLs),' Short URLs extracted'
    
    shortUrlsArray = shortURLs.items()
    count = 0
    while shortUrlsArray:
        subArray = []
        for _ in range(10):
            if shortUrlsArray:
                subArray.append(shortUrlsArray.pop())
        
        longURLs,webpages,webpageUrls,numExpanded = getOrigLongURLs(subArray)
        saveLongUrls(longURLs)
        saveTextToWebpageFiles(webpages, webpageUrls, count)
        
        count = count + numExpanded
        #print 'Finished 10 files'

def addDocsFromDirectory(directory):
    global tweetFileName
    print("directory: " + directory)
    for fn in os.listdir(directory):
        tweetFileName = fn
        fullFileName = os.path.join(directory, fn)
        currentFileName = fn.split('.')[0] 
        if (fullFileName.endswith('json')):
            print "Now processing file " + fn
            processJsonFile(fullFileName)

# EXECUTED AS THE MAIN FUNCTION
# Runs functions in this order: 1) readTweetsFile  2) extractShortURLs 3) extractLongUrls (and webpage text contents)
# To run: python downloadWebpagesFromTweets.py [json file path]
if __name__ == "__main__":
    directory = "C:\\Users\\Michael\\Documents\\VT 2016\\Hypertext\\dataClimateChange\\Sub"
    directory = directory.strip()
    
    addDocsFromDirectory(directory)

	
		
