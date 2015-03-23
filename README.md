# EAC-CPF Indexer Data Processing Utility


EAC-Indexer is a utility for indexing EAC-CPF in a file system or a web site,
and post-processing it for applications such as search and visualization in
maps or timelines. The utility is able to extract concepts, people and
locations from free text or structured data fields. Source and processed data
are written to disk for each stage of processing, to enable an open workflow
and alternative uses.

This is a fork of the original project from the University of Melbourne developed
at the [Brown University Library](http://library.brown.edu/) for indexing the catalog for the [Hall-Hoag collection of dissenting and extremist printed propaganda](http://library.brown.edu/collatoz/info.php?id=62). It adds minor enhancements to the EAC cleaning facility and implements the ability to use user-implemented Python classes to provide parameters to the XSLT stylesheet.

## Credits


EAC-Indexer is a project of the eScholarship Research Center at the University 
of Melbourne. For more information about the project, please contact us at:

 > eScholarship Research Center 
 > University of Melbourne
 > Parkville, Victoria
 > Australia
 > www.esrc.unimelb.edu.au

### Authors:

 * Davis Marques <davis.marques@unimelb.edu.au>
 * Adam Bradley <atb@brown.edu>

### Thanks:

 * GeoPy - http://code.google.com/p/geopy
 * Google Maps API - http://maps.google.com
 * lxml - http://lxml.de
 * Python - http://www.python.org
 * Python Calais - http://code.google.com/p/python-calais
 * PyYAML - http://pyyaml.org


## License

Please see the LICENSE file for license information.


## Installation

Requires Python 2.7.x, geopy, lxml, pyYAML, Simple JSON libraries.

 * pip install geopy
 * pip install lxml
 * pip install pyyaml

To infer data from EAC-CPF files, a free account and associated API key may be
required for the following services:

 * Alchemy - http://www.alchemyapi.com/
 * Google Maps - https://code.google.com/apis/console/
 * OpenCalais - http://www.opencalais.com/


## Usage

Run python Indexer.py -h for a list of options. A configuration file is
required, to specify indexing options. You can copy the included
indexer.cfg.example file to a new location and edit it as needed.


## Known Issues
