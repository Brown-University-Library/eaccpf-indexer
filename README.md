EAC-CPF Indexer Data Processing Utility
=======================================

EAC-Indexer is a utility for indexing EAC-CPF in a file system or a web site,
and post-processing it for applications such as search and visualization in
maps or timelines. The utility is able to extract concepts, people and
locations from free text or structured data fields. Source and processed data
are written to disk for each stage of processing, to enable an open workflow
and alternative uses.


Credits
-------

EAC-Indexer is a project of the eScholarship Research Center at the University 
of Melbourne. For more information about the project, please contact us at:

 > eScholarship Research Center
 > University of Melbourne
 > Parkville, Victoria
 > Australia
 > www.esrc.unimelb.edu.au

Authors:

 * Davis Marques <davis.marques@unimelb.edu.au>
 * Marco La Rosa <marco@larosa.org.au>
  
Thanks:

 * GeoPy - http://code.google.com/p/geopy
 * Google Maps API - http://maps.google.com
 * lxml - http://lxml.de
 * Pairtree - https://pypi.python.org/pypi/Pairtree
 * Python - http://www.python.org
 * Python Calais - http://code.google.com/p/python-calais
 * PyYAML - http://pyyaml.org
 * Simple JSON - https://github.com/simplejson/simplejson


License
-------

Please see the LICENSE file for license information.


Installation
------------

Requires Python 2.7.x with lxml, pyYAML, Pairtree, Simple JSON libraries.

 * pip install lxml
 * pip install pairtree
 * pip install pyyaml
 * pip install simplejson

To infer data from EAC-CPF files, a free account and associated API key is 
required for the following services:

 * Alchemy - http://www.alchemyapi.com/
 * Google Maps - https://code.google.com/apis/console/
 * OpenCalais - http://www.opencalais.com/


Usage
-----

Run python Indexer.py -h for a list of options. Copy the indexer.cfg.example
files to a new location edit it as needed.


Revision History
----------------

1.5.1

 * Additional unit tests throughout
 * Refactoring of modules to simplify testing
 * Added partial copy of FCNS data to enable local testing of modules
 * Added Cfg module to carry globals

1.5.0

 * Send all logging to STDOUT
 * Updated geopy module, switched to OpenStreetMaps for geocoding
 * Can specify a custom EAC-CPF to SID XSLT
 * Resolved problem of XML namespace declarations in EAC-CPF data

1.4.1

* On crawl, add document source, metadata/presentation URLs as attributes to
  the eac-cpf root node
* Transform accepts an optional custom XSLT file
* Transform operation uses source, metadata/presentation URLs from eac-cpf
  root node
* Created ESRC specific EAC-CPF to SID XSLT transform files
* Added support for console execution of Poster.py

1.4.0

 * Updated eaccfp-to-solr.xslt to account for the full note appearing
   directly under biogHist
 * Add update option to process only changed files
 * Added additional logging to make it apparent when the BASE URL value is
   incorrect, or that a resource can't be loaded

1.3.3

 * Improve extracted relations data
 * Store hash and timestamp of all files in a hidden file, to be used with
   update option

1.3.2

 * EACCPF document unit tests and reporting
 * Analysis module writes report file
 * File indexing works solely from the file system

1.3.1

 * DigitalObject module and unit tests
 * Revised digital object indexing to work from EAC-CPF rather than HTML
 * Improved address component parsing 
 * First implementation of EAC-CPF Analyzer with unit tests
 * Moved some modules from source package to Python distribution, noted
   dependencies

1.3.0

 * Fixed unicode handling issues
 * Boost fields as specified in configuration file
 * Image indexing and thumbnail caching
 * HTML indexing
 * Renamed project to eaccpf-indexer
 * Unit tests for various modules

1.2.2

 * Purged configuration files from repository, added them to .gitignore 
 * Processes only EAC-CPF now, and ignores EAC when found
 * Added type option to [infer] to specify inference types to be executed
 * Skips geolocation if GIS attribute is present on the place tag
 * Added scaffolding for unit tests
 * Handles case where geocoding returns multiple locations
 * Moved third party libraries into esrc package

1.2.1

 * Transforms EAC-CPF to Solr Input Document format using an external XSLT file
 * Crawler appends comment to EAC-CPF xml to record source and referrer URLs
 * Removed BeautifulSoup for all applications where data is written because it
   doesn't respect case formatting in tag names
 * Merges inferred data with Solr Input Documents
 * Posts Solr Input Documents to Solr core

1.1.1

 * Converts place names in structured fields into geographic coordinates for
   mapping
 * Writes inferred data to cache folder
 * Extracts entities (people, places, things, concepts) from free text fields

1.1.0

 * Revised application architecture
 * Reads configuration from file
 * Crawls file system for EAC, EAC-CPF files
 * Cleans input data to resolve common XML errors

1.0.0

 * Initial solr-feeder release


Known Issues
------------

