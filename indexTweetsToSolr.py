#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sunburnt
import logging
import hashlib
import sys
import json
import fileinput
import io
import codecs
import os
import re
import ijson

tweetlist = []
i = 0

def indexDocsToSolr(docs):
    global tweetlist, i
    solrDocs = []
    for fromUser,createdAt,doc in docs:
        hash_id = hashlib.md5(doc.encode('ascii',errors='ignore')).hexdigest()
        # missingaddDocsFromDirectory pub_date
        solr_doc = {"id":re.sub(r'[^\w #@//]', '', doc), "text":doc, "content":doc, "type":"Tweet", "from_user":fromUser, "collection_id":currentFileName, "created_at":createdAt}
        solrDocs.append(solr_doc)
        tweetlist.append(hash_id)
        i += 1
    commitToSolr(solrDocs)

def commitToSolr(solrDocs):
    solrURL = "http://nick.dlib.vt.edu:8983/solr/blacklight-core"
    solr_instance = sunburnt.SolrInterface(solrURL)
    solr_instance.add(solrDocs)

    try:
        solr_instance.commit()
    except:
        print "Could not Commit Changes to Solr, check the log files."
        logging.info("Could not Commit Changes to Solr, check the log files.")
    else:
        print "Successfully committed changes"
        logging.info("Successfully committed changes")

        
def replaceAll(file,searchExp,replaceExp):
    i = 0
    f = io.open(file, encoding='utf-8')
    for i, line in enumerate(f):
        if i == 2:
            print line        
            if line.find('\'') == -1:
                print "File already replaced"
                return
            else:
                print "Replaced all single quotes with double quotes in JSON file"
    f.close()

    for line in fileinput.input(file, inplace=1):
        i += 1
        if i == 3:
            if line.find('\''):
                
                break
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)


def processJsonFile(fullFileName):
    docList = []

    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf8')(sys.stderr)
    f = io.open(fullFileName, encoding='utf-8')
    objects = ijson.items(f, 'item')
    for jsonObj in objects:
        fromUser = jsonObj['from_user'] #Created by
        createdAt = jsonObj['created_at']#Created at 
        doc = jsonObj['text'] #text
        docList.append((fromUser,createdAt,doc))

        if len(docList) > 10000:
            indexDocsToSolr(docList)
            docList = []

    indexDocsToSolr(docList)

def addDocsFromDirectory(directory):
    global currentFileName
    print("directory: " + directory)
    for fn in os.listdir(directory):
        fullFileName = os.path.join(directory, fn)
        currentFileName = fn.split('.')[0] 
        if (fullFileName.endswith('json')):
            print "Now processing file " + fn
            replaceAll(fullFileName,"\'",'"')
            processJsonFile(fullFileName)

if __name__ == "__main__":
    directory = "C:\\Users\\Michael\\Documents\\VT 2016\\Hypertext\\dataClimateChange"
    directory = directory.strip()
    
    addDocsFromDirectory(directory)