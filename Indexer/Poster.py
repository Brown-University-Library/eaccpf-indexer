"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

import argparse
import logging
import os
import requests


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
        self.logger = logging.getLogger('Poster')
        
    def commit(self, Url):
        """
        Commit staged data to the Solr core.
        """
        msg = '<commit expungeDeletes="true"/>'
        if Url.endswith('/'):
            url = Url + 'update'
        else:
            url = Url + '/update'
        resp = requests.post(url, msg, headers=self.headers)
        if resp.status_code == 200:
            self.logger.info("Committed staged data to {0}".format(Url))
        else:
            self.logger.error("Commit failed for {0}\n{1}".format(Url, resp.content))

    def flush(self, Url):
        """
        Flush all documents from the Solr core at the specified URL.
        """
        msg = "<delete><query>*:*</query></delete>"
        if Url.endswith('/'):
            url = Url + 'update'
        else:
            url = Url + '/update'
        resp = requests.post(url, msg, headers=self.headers)
        if resp.status_code == 200:
            self.logger.info("Flushed {0}".format(Url))
        else:
            self.logger.error("Flush failed for {0}\n{1}".format(Url, resp.content))

    def optimize(self, Url):
        """
        Optimize data in Solr core.
        """
        # send command
        msg = '<optimize waitSearcher="false"/>'
        if Url.endswith('/'):
            url = Url + 'update'
        else:
            url = Url + '/update'
        resp = requests.post(url, msg, headers=self.headers)
        if resp.status_code == 200:
            self.logger.info("Optimized {0}".format(Url))
        else:
            self.logger.error("Optimize failed for {0}\n{1}".format(Url, resp.content))

    def post(self, Source, Url):
        """
        Post Solr Input Documents in the Source directory to the Solr core if 
        they have all required fields.
        """
        # check state
        assert os.path.exists(Source), self.logger.error("Source path does not exist: {0}".format(Source))
        # ensure that the posting URL is correct
        if Url.endswith('/'):
            url = Url + 'update'
        else:
            url = Url + '/update'
        # post documents
        files = os.listdir(Source)
        for filename in files:
            if filename.endswith(".xml"):
                try:
                    f = open(Source + os.sep + filename)
                    data = f.read()
                    f.close()
                    resp = requests.post(url, data=data, headers=self.headers)
                    if resp.status_code == 200:
                        self.logger.info("Posted {0}".format(filename))
                    else:
                        self.logger.error("Post failed for {0}\n{1}".format(filename, resp.content))
                except:
                    self.logger.error("Post failed for {0}".format(filename), exc_info=True)

    def run(self, Params):
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


if __name__ == '__main__':
    # parse console arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", help="Commit data in the Solr core at the specified URL")
    parser.add_argument("--flush", help="Flush data from the Solr core at the specified URL")
    parser.add_argument("--optimize", help="Optimize data in the Solr core at the specified URL")
    parser.add_argument("--post", help="Post data from the specified source to the Solr core at the specified URL")
    parser.add_argument("source", help="Post data from the specified source to the Solr core at the specified URL", nargs='?')
    args = parser.parse_args()
    # execute actions
    poster = Poster()
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
