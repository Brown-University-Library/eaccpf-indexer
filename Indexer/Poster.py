"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from lxml import etree

import Cfg
import Timer
import argparse
import logging
import os
import requests
import sys


__description__ = """Posts Solr Input Documents to a Solr core. Performs flush, delete, commit and optimize commands."""


class Poster(object):
    """
    Posts Solr Input Documents to a Solr core. Performs post, flush, commit and
    optimize commands.
    @see: http://code.activestate.com/recipes/577909-basic-interface-to-apache-solr/
    """

    def __init__(self, source, url, actions, logger=None):
        self.headers = { 'Content-type': 'text/xml; charset=utf-8' }
        if logger:
            self.log = logger
        else:
            self.log = logging.getLogger()
        # set parameters
        self.actions = actions
        self.source = source
        self.url = url + 'update' if url.endswith('/') else url + '/update'

    def commit(self):
        """
        Commit staged data to the Solr core.
        """
        msg = '<commit expungeDeletes="true"/>'
        resp = requests.post(self.url, msg, headers=self.headers)
        if resp.status_code == 200:
            self.log.info("Committed staged data to {0}".format(self.url))
        else:
            self.log.error("Commit failed for {0}\n{1}".format(self.url, resp.content), exc_info=Cfg.LOG_EXC_INFO)
        return resp.status_code

    def flush(self):
        """
        Flush all documents from the Solr core at the specified URL.
        """
        msg = "<delete><query>*:*</query></delete>"
        resp = requests.post(self.url, msg, headers=self.headers)
        if resp.status_code == 200:
            self.log.info("Flushed {0}".format(self.url))
        else:
            self.log.error("Flush failed for {0}\n{1}".format(self.url, resp.content), exc_info=Cfg.LOG_EXC_INFO)
        return resp.status_code

    def optimize(self):
        """
        Optimize data in Solr core.
        """
        msg = '<optimize waitSearcher="false"/>'
        resp = requests.post(self.url, msg, headers=self.headers)
        if resp.status_code == 200:
            self.log.info("Optimized {0}".format(self.url))
        else:
            self.log.error("Optimize failed for {0}\n{1}".format(self.url, resp.content), exc_info=Cfg.LOG_EXC_INFO)
        return resp.status_code

    def post(self):
        """
        Post Solr Input Documents in the Source directory to the Solr core if
        they have all required fields.
        """
        # check state
        assert os.path.exists(self.source), self.log.error("Source path does not exist: {0}".format(self.source))
        # post documents
        posted = 0
        errors = 0
        for filename in [f for f in os.listdir(self.source) if f.endswith(".xml")]:
            try:
                self.log.debug("Reading {0}".format(filename))
                # load the xml document and strip empty tags
                xml = etree.parse(self.source + os.sep + filename)
                self.strip_empty_elements(xml)
                data = etree.tostring(xml)
                # post the document to the index
                self.log.debug("Posting {0}".format(filename))
                resp = requests.post(self.url, data=data, headers=self.headers)
                if resp.status_code == 200:
                    posted += 1
                    self.log.info("Posted {0}".format(filename))
                else:
                    errors += 1
                    self.log.error("Post failed for {0}\n{1}".format(filename, resp.content))
            except:
                self.log.error("Post failed for {0}".format(filename), exc_info=Cfg.LOG_EXC_INFO)
        # report on the number of documents posted, failed
        self.log.info("Posted {0} documents. {1} errors.".format(posted, errors))

    def run(self):
        """
        Execute processing actions.
        """
        with Timer.Timer() as t:
            for action in self.actions:
                f = getattr(self, action)
                f()
        self.log.info("Poster finished in {0}:{1}:{2}".format(t.hours, t.minutes, t.seconds))

    def strip_empty_elements(self, doc):
        """Remove empty elements from the document.

        Solr date fields don't like to be empty - hence why this
        method exists. As it turns out, it can't hurt to ditch empty
        elements - less to submit. Hence why it's generic

        @params:
        doc: the XML document
        """
        for elem in doc.iter('field'):
            if elem.text is None:
                elem.getparent().remove(elem)


def post(params):
    """
    Execute post actions
    """
    actions = params.get("post", "actions").split(",")
    index = params.get("post", "index")
    source = params.get("post", "input")
    poster = Poster(source, index, actions)
    poster.run()


if __name__ == '__main__':
    # parse console arguments
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("--commit", help="Commit data in the Solr core at the specified URL", action='store')
    parser.add_argument("--flush", help="Flush data from the Solr core at the specified URL")
    parser.add_argument("--optimize", help="Optimize data in the Solr core at the specified URL")
    parser.add_argument("--post", help="Post data to the Solr core at the specified URL")
    parser.add_argument("source", help="Post data from the specified path to the Solr core", nargs='?')
    args = parser.parse_args()
    # configure the poster
    if args.commit:
        action = "commit"
        url = args.commit
    elif args.flush:
        action = "flush"
        url = args.flush
    elif args.optimize:
        action = "optimize"
        url = args.optimize
    elif args.post and args.source:
        action = "post"
        url = args.post
    else:
        parser.print_help()
        sys.exit()
    source = args.source if args.source else None
    # configure logging
    logger = logging.getLogger()
    formatter = logging.Formatter(Cfg.LOG_FORMAT)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    logger.setLevel(logging.DEBUG)
    # execute
    poster = Poster(source, url, [action], logger=logger)
    poster.run()
