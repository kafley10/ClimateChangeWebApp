#!/usr/bin/env python

import os
import sunburnt
import hashlib
import logging
import io
import re

# Usage: python indexToSolr.py [directory path]
# First line of each file must have url

# Default schema: id, text
# Indexing uses document frequency
# Content = stored, used for blurbs also sent to Text  OR  Text (non-optional) = indexed
# Text = also contains the contents of all other fields
solrDocs = []

def addToDocumentList(url, contents, title, folderName):
    url = url.encode('utf-8')
    html_id = hashlib.md5(url).hexdigest()
    solr_doc = {"id":title, "text":contents, "content": contents, "type":"Webpage", "url":url, "collection_id":folderName, "title":title}
    if 'Oil unlikely to ever be fully exploited' in contents:
        print len(contents)
    solrDocs.append(solr_doc)

    return html_id


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
	
def addDocsFromDirectory(directory):
    global solrDocs
    addedIds = []
    i = 0
    print("directory: " + directory)
    for fn in os.listdir(directory):
        fn = os.path.join(directory, fn)
        folderPath = os.path.dirname(fn)
        _,folderName = os.path.split(folderPath)
        f = io.open (fn, 'r', encoding='utf-8')
        url = f.readline()
        title = f.readline()         
        contents = f.read() #read all other lines
        f.close()
        folderName = folderName.split('-')[0] # z163-1000 -> z163
        doc_id = addToDocumentList(url, contents, title, folderName)
        addedIds.append(doc_id + '\n')

        # Commit in batches of 100
        if (i % 100 == 0) and (i != 0):
            commitToSolr(solrDocs)
            print len(solrDocs)
            solrDocs = []
        i += 1
    # Commit the remaining docs
    if len(solrDocs) > 0:
        commitToSolr(solrDocs)

    print 'Creating file with uploaded ids: see ./uploadIds.txt'
    f = io.open('uploadedIds.txt','w', encoding='utf-8')
    for s in addedIds:
        s = s + '\n'
        s = s.decode('utf-8')
        f.write(s)
    f.close()
    
if __name__ == "__main__":
    directory = "C:\\Users\\Michael\\Documents\\VT 2016\\Hypertext\\Webpages\\z297"
    directory = directory.strip()
	
    addDocsFromDirectory(directory)
