#!/usr/bin/env python

import sunburnt
import logging
import hashlib
import sys

# Usage: python indexToSolr.py [formatted solr reference file] [eventName] [archiveID]
# Runs: uploadToSolr -> indexDocsToSolr -> uploadToSolr
# TODO: figure out how to format the reference file

# Default schema: id, text
# Indexing uses document frequency
# Content = stored, used for blurbs also sent to Text  OR  Text (non-optional) = indexed
# Text = also contains the contents of all other fields

# TODO: Use id & content field, will also be saved in text field.
# TODO: Add function that reads html file (a few at a time) and then indexes, repeat till done
# TODO: Add url to first line of html file, change this to parse that line, change url, 

def indexDocsToSolr(docs,indexingOptions):
    solrURL = indexingOptions['solrURL']
    event = indexingOptions['event']
    eventType = indexingOptions['eventType']
    archiveID = indexingOptions['archiveID']
    collType = indexingOptions['collType']
    solr_instance = sunburnt.SolrInterface(solrURL)
    solrDocs = []
    if len(docs) > 0:
        if collType == "web": # we are doing only web initially
            for url,title, doc in docs:
            
                html_id = hashlib.md5(url).hexdigest()
                # Dictionary for solr
                solr_doc = {"id":html_id, "content":doc, "title":title,"collection_type":collType, "collection_id":archiveID, "url":url, "event":event, "event_type":eventType}
                solrDocs.append(solr_doc)
        elif collType == "tweets":
            for html_id,doc in docs:
                solr_doc = {"id":html_id, "content":doc, "collection_type":collType, "collection_id":archiveID, "event":event, "event_type":eventType}
                solrDocs.append(solr_doc)
                # attempt to add it to the index, make sure to commit later
                #try:
        solr_instance.add(solrDocs)
                #except Exception as inst:
                #    print "Error indexting file, with message" + str(inst)
    
        try:
            solr_instance.commit()
        except:
            print "Could not Commit Changes to Solr, check the log files."
            logging.info("Could not Commit Changes to Solr, check the log files.")
        else:
            print "Successfully committed changes"
            logging.info("Successfully committed changes")
    else:
        print "No documents to index"
        

# TODO: Change relfile to be directory of all html files to read
def uploadToSolr(relfile, eventName, archiveID):
    f = open (relfile, 'r')
   # i = 0
    title = None
    url = None
    doc = None
    docList = []
  #  z = 0
 '''
    for line in f:
        if i % 2 == 0:
            try:
                title,_,url = line.strip().split("\t")
            except Exception as e:
                _,url = line.strip().split("\t")
                title = eventName
                print line.strip()
                z += 1
        else:
            doc = line.strip()
            docList.append((url,title,doc)) # syntax of a tuple
            doc = None
            url = None
            title = None
        i += 1
'''
    print "Len doclist : " , len(docList)
    solrKeys = {}
    solrKeys['solrURL'] = "http://nick.dlib.vt.edu:8983/solr/blacklight-core" # TODO: Check email. change if necessary
    #solrKeys['collType'] = "web"
    #solrKeys['event'] = eventName
    #solrKeys['eventType'] = "School Shootings"
    #solrKeys['archiveID'] = archiveID
    indexDocsToSolr(docList,solrKeys)
    f.close()
    print z

if __name__ == "__main__":
    relfile = sys.argv[1].strip()
    #eventName = sys.argv[2].strip()
    #archiveID = sys.argv[3].strip()

    
	#print "Event name : " + eventName
    #print "archive ID : " + archiveID
    uploadToSolr(relfile, eventName,archiveID)