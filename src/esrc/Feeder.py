'''
This file is subject to the terms and conditions defined in the
'LICENSE.txt' file, which is part of this source code package.
'''

import argparse
import sys

class Feeder():
    '''
    Harvests metadata from a file system or the web, processes it and then 
    posts that data to an Apache Solr/Lucene index.
    '''
    
    # configuration options
    options = {}
    
    # configure command line options
    parser = argparse.ArgumentParser(description="Harvest, process, and post metadata to Apache Solr/Lucene index.")
    parser.add_argument('config', help="Read configuration file from specified path")
    parser.add_argument('-s','--scrub', help="Clean XML files of common errors before further processing", action="store_true", default=False)
    parser.add_argument('-i','--infer', help="Infer concepts, entities, location, date ranges from data")
    parser.add_argument('-l','--log', help="Write log data to specified path")
    parser.add_argument('-o','--output', help="Write Solr Input Document to specified path")
    parser.add_argument('-r','--report', help="Write a report on indexing activity and quality of data to the specified path")
    parser.add_argument('-t','--test', help="Execute actions without posting data to Solr", action="store_true", default=False)
    parser.add_argument('-v','--verbose', help="Write logging messages to standard output", action="store_true", default=False)
    
    args = parser.parse_args()
 
    def load(self):
        '''
        Load and parse configuration file
        '''
        pass
 
    def run(self):
        '''
        '''
        pass


if __name__ == '__main__':
    main = Feeder()
    main.run()