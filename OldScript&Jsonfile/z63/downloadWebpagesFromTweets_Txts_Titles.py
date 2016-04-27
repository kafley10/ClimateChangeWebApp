import requests
from bs4 import BeautifulSoup, Comment
from contextlib import closing
import sys
import re
import json
requests.packages.urllib3.disable_warnings()

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
    
def extractText_TitleFromHTML(webpages):
    soup = BeautifulSoup(webpages)
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
    for surl,v in shortURLs:
        try:
            with closing(requests.get(surl.strip(), verify=False)) as r:
                #print r.status_code
                if r.status_code == requests.codes.ok:
                    #print surl
                    ori_url =r.url
                    webpages.append(r.text)
                    if ori_url in expandedURLs:
                        expandedURLs[ori_url].append((surl,v))
                    else:
                        expandedURLs[ori_url] = [(surl,v)]
                    #expandedURLs.append(ori_url)
                    i  =i+1
                else:
                    e = e+1    
                    print r.status_code , surl, r.url, r.request.url
                    #expandedURLs.append("")
        except :
            print sys.exc_info()[0], surl
            #expandedURLs.append("")
            e = e +1
    print "urls expanded: ", i
    print "bad Urls: ",e
    return expandedURLs,webpages

# Input: the file location of a tweets JSON file, extracts the text field of each JSON object.
# Output: a local array of the texts of each tweet.
def readTweetsFile(tweetsFile):
	with open(tweetsFile,'r') as f:
		tweets = f.read()
	
	tweets = json.loads(tweets.replace("\'", '"'))
	print len(tweets)
	
	texts = {}
	for tweet in tweets:
		if 'id' in tweet:
			if 'text' in tweet:
				texts[tweet['id']] = tweet['text']
			
	print len(texts)
	return texts.values()


# EXECUTED AS THE MAIN FUNCTION
# Runs functions in this order: 1) readTweetsFile  2) extractShortURLs 3) extractLongUrls (and webpage text contents)
# To run: python downloadWebpagesFromTweets.py [json file path]
if __name__ == "__main__":
	tweetFileName = "z63-1000.json"
	'''
	#with open(tweetFileName,'r') as fr:
	#	tweets = fr.readlines()
	import csv
	with open(tweetFileName, 'rU') as csvfile:
		tweetsCSV = csv.reader(csvfile)
		tweets = []
		for t in tweetsCSV:
			tweets.append(t)
	print len(tweets)
	
	tweetsTxt = [tw[0] for tw in tweets]
	'''
	tweetsTxt = readTweetsFile(tweetFileName)
	shortURLs = extractShortURLsFreqDic(tweetsTxt)
	f = open(tweetFileName.split(".")[0] + '-ShortURLs.txt','w')
	f.write("\n".join(shortURLs.keys()))
	f.close()
	print len(shortURLs),' Short URLs extracted'
	
	longURLs,webpages = getOrigLongURLs(shortURLs.items())
	if longURLs:
		f = open(tweetFileName.split(".")[0] + '-LongURLs.txt','w')
		f.write("\n".join(longURLs.keys()))
		f.close()
		print len(longURLs),' Long URLs retrieved'
	else:
		print 'No Long URLs'
	if webpages:
		wpsTxts = []
		wpsTitles = []
		for wp in webpages:
			wpTxt,wpTitle = extractText_TitleFromHTML(wp)
			wpsTxts.append(wpTxt)
			wpsTitles.append(wpTitle)
		print 'Saving webpages'
		for i in range(len(webpages)): # Create text file for each webpage: 0.txt will have the 1st webpage
			with open(str(i)+'.txt','w') as fw:
				fw.write(webpages[i].encode('utf8'))
		print 'done'
	else:
		print 'NO webpages'
		
