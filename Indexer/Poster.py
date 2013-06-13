"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from lxml import etree
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
        
    def _hasRequiredFields(self, Doc, Fields):
        """
        Determine if the XML document has one or more instances of the required
        fields.
        """
        for field in Fields:
            x = Doc.findall(".//field",{'name':field})
            if x == None or len(x) < 1:
                return False
        return True

    def commit(self, Solr):
        """
        Commit staged data to the Solr core.
        """
        msg = '<commit expungeDeletes="true"/>'
        if Solr.endswith('/'):
            url = Solr + 'update'
        else:
            url = Solr + '/update'
        resp = requests.post(url, msg, headers=self.headers)
        if resp.status_code == 200:
            self.logger.info("Committed staged data to " + Solr)
        else:
            self.logger.error("Something went wrong trying to commit the changes.")
            self.logger.error("\n%s" % resp.text)

    def flush(self, Solr):
        """
        Flush all documents from Solr.
        """
        msg = "<delete><query>*:*</query></delete>"
        if Solr.endswith('/'):
            url = Solr + 'update'
        else:
            url = Solr + '/update'
        resp = requests.post(url, msg, headers=self.headers)
        if resp.status_code == 200:
            self.logger.info("Flushed data from " + Solr)
        else:
            self.logger.error("Something went wrong trying to submit a request to wipe the index.")
            self.logger.error("\n%s" % resp.text)

    def optimize(self, Solr):
        """
        Optimize data in Solr core.
        """
        # send command
        msg = '<optimize waitSearcher="false"/>'
        if Solr.endswith('/'):
            url = Solr + 'update'
        else:
            url = Solr + '/update'
        resp = requests.post(url, msg, headers=self.headers)
        if resp.status_code == 200:
            self.logger.info("Optimized " + Solr)
        else:
            self.logger.error("Something went wrong trying to optimize the index.")
            self.logger.error("\n%s" % resp.text)

    def post(self, Source, Solr, Fields):
        """
        Post Solr Input Documents in the Source directory to the Solr core if 
        they have all required fields.
        """
        # check state
        assert os.path.exists(Source), self.logger.warning("Source path does not exist: " + Source)
        # ensure that the posting URL is correct
        if Solr.endswith('/'):
            url = Solr + 'update'
        else:
            url = Solr + '/update'
        # post documents
        files = os.listdir(Source)
        for filename in files:
            if filename.endswith(".xml"):
                try:
                    xml = etree.parse(Source + os.sep + filename)
                    doc = xml.getroot()
                    if self._hasRequiredFields(doc,Fields):
                        data = etree.tostring(doc)
                        resp = requests.post(url, data=data, headers=self.headers)
                        if resp.status_code == 200:
                            self.logger.info("Posted " + filename)
                        else:
                            self.logger.error("Submission of %s failed with error %s." % (filename, resp.status_code))
                except:
                    self.logger.warning("Could not complete post operation for " + filename, exc_info=True)

    def run(self, Params):
        """
        Post Solr Input Documents to Solr core and perform index maintenance 
        operations.
        """
        actions = Params.get("post","actions").split(",")
        index = Params.get("post","index")
        source = Params.get("post","input")
        if Params.has_option("post", "required"):
            required = Params.get("post","required").split(',')
        else:
            required = []
        # execute actions
        if 'flush' in actions:
            self.flush(index)
        if 'post' in actions:
            self.post(source,index,required)
        if 'commit' in actions:
            self.commit(index)
        if 'optimize' in actions:
            self.optimize(index)
