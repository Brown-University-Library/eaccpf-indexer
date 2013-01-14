'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

import argparse
import logging
import sys
import ConfigParser
from Cleaner import Cleaner
from Crawler import Crawler
from Facter import Facter
from Poster import Poster
from Reporter import Reporter
from Transformer import Transformer

class Feeder(object):
    '''
    Harvests EAC files from a file system or the web, processes them and then 
    posts that data to an Apache Solr/Lucene index.
    '''
    
    def __init__(self):
        '''
        Set logging options, parse the command line arguments, load the 
        configuration file.
        '''
        # logging default
        formatter = logging.Formatter('%(asctime)s - %(filename)s %(lineno)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('feeder')
        self.logger.setLevel(level=logging.INFO)
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        self.logger.addHandler(sh)
        # configure command line options
        self.parser = argparse.ArgumentParser(description="Harvest, process, and post EAC-CPF metadata to Apache Solr/Lucene index.")
        self.parser.add_argument('config', help="Path to configuration file")
        self.parser.add_argument('--clean', help="Clean input files of common errors before further processing", action='store_true')
        self.parser.add_argument('--crawl', help="Crawl file system or web site for metadata files", action='store_true')
        self.parser.add_argument('--infer', help="Infer concepts, entities, locations from free text fields", action='store_true')
        self.parser.add_argument('--post', help="Post Solr Input Documents to Apache Solr index", action='store_true')
        self.parser.add_argument('--report', help="Generate a report and write to specified path", action='store_true')
        self.parser.add_argument('--transform', help="Transform EAC, EAC-CPF files to Solr Input Document format", action='store_true')
        ## self.parser.add_argument('--fix', help="Fix common errors in HTML or XML source files and update the source files where possible.", action='store_true')
        # parse the command line arguments
        try:
            self.args = self.parser.parse_args()
            self.logger.info('Started Feeder with ' + ' '.join(sys.argv[1:]))
        except Exception, e:
            self.parser.print_help()
            sys.exit(e)
        # load the specified configuration file
        try:
            self.config = ConfigParser.SafeConfigParser()
            self.config.readfp(open(self.args.config))
        except Exception, e:
            self.logger.critical("Could not load the specified configuration file")
            sys.exit(e)
 
    def run(self):
        '''
        Start processing.
        '''
        # if crawl
        if (self.args.crawl):
            crawler = Crawler()
            crawler.run(self.config)
        # if clean
        if (self.args.clean):
            cleaner = Cleaner()
            cleaner.run(self.config)
        # if fix
        #if (self.args.fix):
        #    self.logger.warning("Fix option not implemented yet")
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
            poster.run()
        # if report
        if (self.args.report):
            reporter = Reporter()
            reporter.run(self.config)
        # done
        self.logger.info("Finished job")

# entry point
if __name__ == '__main__':
    feeder = Feeder()
    feeder.run()
   
    