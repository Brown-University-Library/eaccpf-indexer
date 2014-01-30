"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

import Cfg
import ConfigParser
import argparse
import datetime
import logging
import sys


class Indexer(object):
    """
    A utility class for indexing EAC-CPF and related content from a web site or 
    file system, inferring data, post-processing and posting that data to an 
    Apache Solr search index.
    """

    def __init__(self):
        # configuration file parser
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
        self.parser.add_argument('--stacktrace', help="display stack trace when an error occurs", action='store_true', dest='trace')
        self.parser.add_argument('--no-stacktrace', help="do not display stack trace when an error occurs", action='store_false', dest='trace')
        # defaults
        self.parser.set_defaults(trace=False)
        self.parser.set_defaults(update=False)
        self.update = False

    def configureLogging(self):
        """
        Configure logging with console stream handler.
        """
        self.logger = logging.getLogger()
        formatter = logging.Formatter(Cfg.LOG_FORMAT)
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(formatter)
        # set the logging level on both the logger and the handler
        if self.args.loglevel and self.args.loglevel == 'DEBUG':
            level = logging.DEBUG
        elif self.args.loglevel and self.args.loglevel == 'INFO':
            level = logging.INFO
        else:
            level = logging.ERROR
        sh.setLevel(level)
        self.logger.addHandler(sh)
        self.logger.setLevel(level)

    def run(self):
        """
        Start processing.
        """
        # parse the command line arguments and set logging options
        try:
            self.args = self.parser.parse_args()
            self.configureLogging()
            self.logger.info("Started with {0}".format(' '.join(sys.argv[1:])))
        except Exception, e:
            self.parser.print_help()
            sys.exit(e)
        # load the configuration file
        try:
            with open(self.args.config) as f:
                self.config.readfp(f)
        except Exception, e:
            self.logger.critical("Could not load the specified configuration file")
            sys.exit(e)
        # set options
        Cfg.LOG_EXC_INFO = self.args.trace
        # start clock
        start = datetime.datetime.now()
        # execute commands
        if (self.args.crawl):
            import Crawler
            Crawler.crawl(self.config, self.args.update)
        if (self.args.clean):
            import Cleaner
            Cleaner.clean(self.config, self.args.update)
        if (self.args.infer):
            import Facter
            Facter.infer(self.config, self.args.update)
        if (self.args.graph):
            import Grapher
            Grapher.graph(self.config, self.args.update)
        if (self.args.transform):
            import Transformer
            Transformer.transform(self.config)
        if (self.args.post):
            import Poster
            Poster.post(self.config)
        if (self.args.analyze):
            import Analyzer
            Analyzer.analyze(self.config, self.args.update)
        # stop clock
        delta = datetime.datetime.now() - start
        s = delta.seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.logger.info("Job finished in {0}:{1}:{2}".format(hours, minutes, seconds))

# entry point
if __name__ == '__main__':
    indexer = Indexer() 
    indexer.run()
