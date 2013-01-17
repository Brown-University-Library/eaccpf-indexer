EAC-CPF Web Crawler and Data Processing Utility
===============================================

EAC-Crawler is a utility for harvesting EAC-CPF from a file system or the 
Internet, and post-processing it for applications such as search and
visualization in maps or timelines. The utility is able to extract concepts, 
people and locations from free text or structured data fields. Source and 
processed data are written to disk for each stage of processing, to enable
an open workflow and alternative uses.


Credits
-------

EAC-Crawler is a project of the eScholarship Research Center at the University 
of Melbourne. For more information about the project, please contact us at:

  eScholarship Research Center
  University of Melbourne
  Parkville, Victoria
  Australia
  www.esrc.unimelb.edu.au

Authors:

 * Davis Marques <davis.marques@unimelb.edu.au>
 * Marco La Rosa <marco@larosa.org.au>
  
Thanks:

 * Alchemy API - http://www.alchemy.com
 * GeoPy - http://code.google.com/p/geopy
 * Google Maps API - http://maps.google.com
 * lxml - http://lxml.de
 * Natural Language Toolkit - http://nltk.org
 * Python - http://www.python.org
 * Python Calais - http://code.google.com/p/python-calais
 * PyYAML - http://pyyaml.org
 * Simple JSON - https://github.com/simplejson/simplejson


License
-------

Please see the LICENSE file for licence information.


Installation
------------

Requires Python 2.7.x, lxml, pyYAML, Simple JSON.


Usage
-----

The crawler is run from the command line. Starting at the seed page or pages, it 
will visit all pages within the seed domain that are linked to that starting 
page. Where an HTML page provides an EAC alternate representation, the crawler 
will fetch, parse and transform the EAC document into a Solr Input Document, 
then insert the record into Solr.  In addition, the crawler can generate a 
report on the quality of the EAC that is indexed.

  python feeder.py config [OPTIONS]
	
  --clean 	   Clean input files of common errors before further processing
  --crawl	   Crawl file system or web site for metadata files
  --infer	   Infer concepts, entities, locations from free text fields
  --post	   Post Solr Input Documents to Apache Solr index
  --report	   Generate a report and write to specified path
  --transform  Transform EAC, EAC-CPF files to Solr Input Document format


Revision History
----------------

1.3.1
? Consider fixing broken source HTML, etc. files in place
? Improve extracted relations data
? Implement entity extraction with Alchemy API
? Transform operation should optionally exclude inferred data
? Updates should optionally be executed only on changed files
? Need to handle the presence of GIS attribute appropriately
? Add stopwatch function to time the duration of processing

1.2.2
? Posts Solr Input Documents to Solr core
? Writes processing messages to report log
? Analyzes EAC data for quality indicators
? Merges individual reports into a single report file

1.2.1
- Transforms EAC to Solr Input Document format using an external XSLT file
- Crawler appends comment to EAC xml to record store source and referrer URLs
- Removed BeautifulSoup for all applications where data is written because it doesn't respect case formatting in tag names
? Merges inferred data with Solr Input Documents
? Requires update to the Solr index configuration
? Handles case where geocoding returns multiple locations

1.1.1
- Converts place names in structured fields into geographic coordinates for mapping
- Writes inferred data to cache folder
- Extracts entities (people, places, things, concepts) from free text fields

1.1.0
- Revised application architecture
- Reads configuration from file
- Crawls file system for EAC, EAC-CPF files
- Cleans input data to resolve common XML errors

1.0.0
- Initial solr-feeder release
