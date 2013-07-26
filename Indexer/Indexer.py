"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

import ConfigParser
import argparse
import datetime
import logging
import os
import sys


class Indexer(object):
    """
    A utility class for indexing EAC-CPF and related content from a web site or 
    file system, inferring data, post-processing and posting that data to an 
    Apache Solr search index.
    """

    def __init__(self):
        """
        Set logging options, create a configuration file parser, command line
        argument parser.
        """
        # configuration parser
        self.config = ConfigParser.SafeConfigParser()
        # configure command line options
        self.parser = argparse.ArgumentParser(description="Harvest, process, and post metadata to an Apache Solr index.")
        self.parser.add_argument('config', help="path to configuration file")
        self.parser.add_argument('--analyze',
                                 help="analyze data",
                                 action='store_true')
        self.parser.add_argument('--clean',
                                 help="clean metadata files of common errors and write updated files",
                                 action='store_true')
        self.parser.add_argument('--crawl',
                                 help="crawl file system or web site for metadata files",
                                 action='store_true')
        self.parser.add_argument('--graph',
                                 help="build graph representation of document collection",
                                 action='store_true')
        self.parser.add_argument('--infer',
                                 help="infer concepts, entities, locations from metadata",
                                 action='store_true')
        self.parser.add_argument('--post',
                                 help="post metadata to Apache Solr index",
                                 action='store_true')
        self.parser.add_argument('--transform',
                                 help="transform metadata to Solr Input Document format",
                                 action='store_true')
        self.parser.add_argument('--update',
                                 help="process only those files that have changed since the last run",
                                 action='store_true')
        self.parser.add_argument('--loglevel',
                                 help="set the logging level",
                                 choices=['DEBUG','INFO','ERROR'],
                                 )
        # defaults
        self.logger = logging.getLogger('')
        self.logger.setLevel(logging.INFO) # don't know why this has to be set but its the only way I can get it to work
        self.logFilePath = '/var/log/indexer.log'
        self.logFormat = '%(asctime)s - %(filename)s %(lineno)03d - %(levelname)s - %(message)s'
        self.update = False

    def _configureLogging(self):
        """
        Configure logging.
        """
        # console stream handler
        formatter = logging.Formatter(self.logFormat)
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(logging.INFO)
        self.logger.addHandler(sh)
        # log file handler
        fh = None
        if os.access('/var/log', os.W_OK):
            import logging.handlers as lh
            fh = lh.RotatingFileHandler(self.logFilePath, backupCount=5, maxBytes=67108864) # 64 MB rollover
            fh.setFormatter(formatter)
            fh.setLevel(logging.INFO)
            self.logger.addHandler(fh)
        # override default log level with user specified value
        if self.args.loglevel:
            if self.args.loglevel == 'DEBUG':
                sh.setLevel(logging.DEBUG)
                if fh:
                    fh.setLevel(logging.DEBUG)
            elif self.args.loglevel == 'INFO':
                sh.setLevel(logging.INFO)
                if fh:
                    fh.setLevel(logging.INFO)
            elif self.args.loglevel == 'ERROR':
                sh.setLevel(logging.ERROR)
                if fh:
                    fh.setLevel(logging.ERROR)

    def run(self):
        """
        Start processing.
        """
        # parse the command line arguments and set logging
        try:
            self.args = self.parser.parse_args()
            self._configureLogging()
            self.logger.info('Started with ' + ' '.join(sys.argv[1:]))
        except Exception, e:
            self.parser.print_help()
            sys.exit(e)
        # load the configuration file
        try:
            self.config.readfp(open(self.args.config))
        except Exception, e:
            self.logger.critical("Could not load the specified configuration file")
            sys.exit(e)
        # set the update option
        if self.args.update:
            self.update = self.args.update
        # start clock
        start = datetime.datetime.now()
        # if crawl
        if (self.args.crawl):
            import Crawler
            crawler = Crawler.Crawler()
            crawler.run(self.config, self.update)
        # if clean
        if (self.args.clean):
            import Cleaner
            cleaner = Cleaner.Cleaner()
            cleaner.run(self.config, self.update)
        # if infer
        if (self.args.infer):
            import Facter
            factor = Facter.Facter()
            factor.run(self.config, self.update)
        # if graph
        if (self.args.graph):
            import Grapher
            grapher = Grapher.Grapher()
            grapher.run(self.config, self.update)
        # if transform
        if (self.args.transform):
            import Transformer
            transformer = Transformer.Transformer()
            transformer.run(self.config)
        # if post
        if (self.args.post):
            import Poster
            poster = Poster.Poster()
            poster.run(self.config)
        # if analyze
        if (self.args.analyze):
            import Analyzer
            analyzer = Analyzer.Analyzer()
            analyzer.run(self.config, self.update)
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
