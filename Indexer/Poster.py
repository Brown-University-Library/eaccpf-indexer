"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from lxml import etree

import Cfg
import argparse
import logging
import os
import requests


__description__ = """Posts Solr Input Documents to a Solr core. Performs flush, delete, commit and optimize commands."""


class Poster(object):
    """
    Posts Solr Input Documents to a Solr core. Performs delete, commit and 
    optimize commands.
    @see: http://code.activestate.com/recipes/577909-basic-interface-to-apache-solr/
    """

    def __init__(self):
        """
        Constructor
        """
        self.headers = { 'Content-type': 'text/xml; charset=utf-8' }
        self.logger = logging.getLogger()

    def commit(self, Url):
        """
        Commit staged data to the Solr core.
        """
        msg = '<commit expungeDeletes="true"/>'
        url = Url + 'update' if Url.endswith('/') else Url + '/update'
        resp = requests.post(url, msg, headers=self.headers)
        if resp.status_code == 200:
            self.logger.info("Committed staged data to {0}".format(Url))
        else:
            self.logger.error("Commit failed for {0}\n{1}".format(Url, resp.content), exc_info=Cfg.LOG_EXC_INFO)
        return resp.status_code

    def flush(self, Url):
        """
        Flush all documents from the Solr core at the specified URL.
        """
        msg = "<delete><query>*:*</query></delete>"
        url = Url + 'update' if Url.endswith('/') else Url + '/update'
        resp = requests.post(url, msg, headers=self.headers)
        if resp.status_code == 200:
            self.logger.info("Flushed {0}".format(Url))
        else:
            self.logger.error("Flush failed for {0}\n{1}".format(Url, resp.content), exc_info=Cfg.LOG_EXC_INFO)
        return resp.status_code

    def optimize(self, Url):
        """
        Optimize data in Solr core.
        """
        msg = '<optimize waitSearcher="false"/>'
        url = Url + 'update' if Url.endswith('/') else Url + '/update'
        resp = requests.post(url, msg, headers=self.headers)
        if resp.status_code == 200:
            self.logger.info("Optimized {0}".format(Url))
        else:
            self.logger.error("Optimize failed for {0}\n{1}".format(Url, resp.content), exc_info=Cfg.LOG_EXC_INFO)
        return resp.status_code

    def post(self, Source, Url):
        """
        Post Solr Input Documents in the Source directory to the Solr core if
        they have all required fields.
        """
        # check state
        assert os.path.exists(Source), self.logger.error("Source path does not exist: {0}".format(Source))
        # ensure that the posting URL is correct
        url = Url + 'update' if Url.endswith('/') else Url + '/update'
        # post documents
        files = os.listdir(Source)
        for filename in files:
            try:
                self.logger.debug("Reading {0}".format(filename))
                # load the xml document and strip empty tags
                xml = etree.parse(Source + os.sep + filename)
                self.strip_empty_elements(xml)
                data = etree.tostring(xml)
                # post the document to the index
                self.logger.debug("Posting {0}".format(filename))
                resp = requests.post(url, data=data, headers=self.headers)
                if resp.status_code == 200:
                    self.logger.info("Posted {0}".format(filename))
                else:
                    self.logger.error("Post failed for {0}\n{1}".format(filename, resp.content))
            except:
                self.logger.error("Post failed for {0}".format(filename), exc_info=Cfg.LOG_EXC_INFO)

    def run(self, Params, StackTrace=False):
        """
        Post Solr Input Documents to Solr core and perform index maintenance 
        operations.
        """
        actions = Params.get("post", "actions").split(",")
        index = Params.get("post", "index")
        source = Params.get("post", "input")
        # execute actions
        if 'flush' in actions:
            self.flush(index)
        if 'post' in actions:
            self.post(source, index)
        if 'commit' in actions:
            self.commit(index)
        if 'optimize' in actions:
            self.optimize(index)

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


if __name__ == '__main__':
    # parse console arguments
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("--commit", help="Commit data in the Solr core at the specified URL", action='store')
    parser.add_argument("--flush", help="Flush data from the Solr core at the specified URL")
    parser.add_argument("--optimize", help="Optimize data in the Solr core at the specified URL")
    parser.add_argument("--post", help="Post data from the specified file source to the Solr core at the specified URL")
    parser.add_argument("source", help="Post data from the specified source to the Solr core at the specified URL", nargs='?')
    args = parser.parse_args()
    # execute actions
    poster = Poster()
    poster.logger.setLevel(logging.DEBUG)
    if args.commit:
        poster.commit(args.commit)
    elif args.flush:
        poster.flush(args.flush)
    elif args.optimize:
        poster.optimize(args.optimize)
    elif args.post and args.source:
        poster.post(args.source, args.post)
    else:
        parser.print_help()

