# ClimateChangeWebApp
The Ideal Climate Change is a digital library and search engine project. It aims to provide an efficient way for graduate students and researchers to search and access archived tweets and web pages related to climate change. It will allow them to utilize the enormous collection of climate change data. Instead of being a complete (end-user ready) application, the project aims to be a starting point for developers who would like to expand on the current progress. The application consists of data containing tweets and webpages that have been extracted and indexed to Solr. The results of user search is organized and displayed on the interface provided by Blacklight.  

This report aims to highlight the design and software requirements of the application to demonstrate the scope, functional requirements, data decomposition, design rationale, and usability; a developer’s manual to provide implementation descriptions, major tasks, timeline, hardware and software requirements, staff requirements, and acceptance criteria to future developers who want to expand on the current progress; a user’s manual to inform stakeholders about user roles, communication methods, rollout considerations, and application glossary; prototype and refinement to explain various components and prototypes of the application; and finally a summary of tests performed and lessons learned. 

It can be concluded that the user has been provided with an efficient tool, which can currently help them search a bulk of archived data. There are a lot of prospective features that can be implemented to enhance the application. For example, a personalized user experience with search recommendations based on search-history. Enhancements like this will be a great project for future Hypertext and Multimedia students to learn about searching, indexing, Artificial Intelligence, and Machine Learning.


SOLR Admin Page:
http://nick.dlib.vt.edu:8983/solr/

Blacklight Core Page:
http://nick.dlib.vt.edu:8983/solr/#/blacklight-core

Search Page:
http://nick.dlib.vt.edu:3000


SOLR Queries:

Delete all indexes & commit:
http://nick.dlib.vt.edu:8983/solr/blacklight-core/update?stream.body=%3Cdelete%3E%3Cquery%3E*:*%3C/query%3E%3C/delete%3E&commit=true

Commit only:
http://nick.dlib.vt.edu:8983/solr/blacklight-core?commit=true
