'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from Analyzer import Analyzer
from Cleaner import Cleaner
from Crawler import Crawler
from Facter import Facter
from Poster import Poster
from Transformer import Transformer

import ConfigParser
import argparse
import datetime
import logging
import sys

class Indexer(object):
    '''
    A utility class for indexing EAC-CPF and related content from a web site or 
    file system, inferring data, post-processing and posting that data to an 
    Apache Solr search index.
    '''

    def __init__(self):
        '''
        Set logging options, parse the command line arguments, load the 
        configuration file.
        '''
        # logging default
        formatter = logging.Formatter('%(asctime)s - %(filename)s %(lineno)03d - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('Indexer')
        self.logger.setLevel(level=logging.INFO)
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        self.logger.addHandler(sh)
        # configuration parser
        self.config = ConfigParser.SafeConfigParser()
        # configure command line options
        self.parser = argparse.ArgumentParser(description="Harvest, process, and post metadata to an Apache Solr/Lucene index")
        self.parser.add_argument('config', help="path to configuration file")
        self.parser.add_argument('--analyze', help="analyze data", action='store_true')
        self.parser.add_argument('--clean', help="clean metadata files of common errors and write updated files", action='store_true')
        self.parser.add_argument('--crawl', help="crawl file system or web site for metadata files", action='store_true')
        self.parser.add_argument('--infer', help="infer concepts, entities, locations from metadata", action='store_true')
        self.parser.add_argument('--post', help="post Solr Input Documents to index", action='store_true')
        self.parser.add_argument('--transform', help="transform metadata to Solr Input Document format", action='store_true')
        self.parser.add_argument('--update', help="process only those files that have changed since the last run", action='store_true')
    
    def run(self):
        '''
        Start processing.
        '''
        # parse the command line arguments
        try:
            self.args = self.parser.parse_args()
            self.logger.info('Started with ' + ' '.join(sys.argv[1:]))
        except Exception, e:
            self.parser.print_help()
            sys.exit(e)
        # load the specified configuration file
        try:
            self.config.readfp(open(self.args.config))
        except Exception, e:
            self.logger.critical("Could not load the specified configuration file")
            sys.exit(e)
        # start clock
        start = datetime.datetime.now()
        # if crawl
        if (self.args.crawl):
            crawler = Crawler()
            crawler.run(self.config)
        # if clean
        if (self.args.clean):
            cleaner = Cleaner()
            cleaner.run(self.config)
        # if infer
        if (self.args.infer):
            factor = Facter()
            factor.run(self.config)
        # if transform
        if (self.args.transform):
            transformer = Transformer()
            transformer.run(self.config)
        # if post
        if (self.args.post):
            poster = Poster()
            poster.run(self.config)
        # if analyze
        if (self.args.analyze):
            analyzer = Analyzer()
            analyzer.run(self.config)
        # stop clock
        delta = datetime.datetime.now() - start
        s = delta.seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        msg = 'Job finished in %s:%s:%s' % (hours, minutes, seconds)
        self.logger.info(msg)    

# entry point
if __name__ == '__main__':
    indexer = Indexer() 
    indexer.run()
