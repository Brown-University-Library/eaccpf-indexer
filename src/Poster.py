'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from httplib2 import Http
from lxml import etree

import logging
import os 

class IndexingError(Exception):
    
    def __init__(self, resp, content):
        self.status = "Server response status: " + resp['status']
        self.content = content

    def __str__(self):
        return repr(self.status)
        return repr(self.content)

class Poster(object):
    '''
    Posts Solr Input Documents to a Solr core. Performs delete, commit and 
    optimize commands.
    @author: Davis Marques
    @author: Marco La Rosa
    @author: ActiveState
    @see: http://code.activestate.com/recipes/577909-basic-interface-to-apache-solr/
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('Poster')
        
    def _hasRequiredFields(self, Doc, Fields):
        '''
        Determine if the XML document has one or more instances of the required
        fields.
        '''
        for field in Fields:
            x = Doc.findall(".//field",{'name':field})
            if x == None or len(x) < 1:
                return False
        return True

    def commit(self, Solr):
        '''
        Commit staged data to the Solr core.
        '''
        # send command
        msg = '<commit waitFlush="false" waitSearcher="false" expungeDeletes="true"/>'
        if Solr.endswith('/'):
            url = Solr + 'update'
        else:
            url = Solr + '/update'
        (resp, content) = Http().request(url, "POST", msg)
        if resp['status'] != '200':
            raise IndexingError(resp, content)
        self.logger.info("Commited staged data to " + Solr)
        return resp, content

    def flush(self, Solr):
        """
        Flush all documents from Solr.
        """
        # send command
        msg = "<delete><query>*</query></delete>"
        if Solr.endswith('/'):
            url = Solr + 'update'
        else:
            url = Solr + '/update'
        (resp, content) = Http().request(url, "POST", msg)
        if resp['status'] != '200':
            print content
            raise IndexingError(resp, content)
        self.logger.info("Flushed data from " + Solr)
        return (resp, content)
        
    def optimize(self, Solr):
        '''
        Optimize data in Solr core.
        '''
        # send command
        msg = '<optimize waitSearcher="false"/>'
        if Solr.endswith('/'):
            url = Solr + 'update'
        else:
            url = Solr + '/update'
        (resp, content) = Http().request(url, "POST", msg)
        if resp['status'] != '200':
            raise IndexingError(resp, content)
        self.logger.info("Optimized " + Solr)
        return (resp, content)
        
    def post(self, Source, Solr, Fields):
        '''
        Post Solr Input Documents in the Source directory to the Solr core if 
        they have all required fields.
        '''
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
                        (resp, content) = Http().request(url, "POST", data)
                        if resp['status'] != '200':
                            raise IndexingError(resp, content)
                        self.logger.info("Posted " + filename + " to Apache Solr")
                except IOError:
                    self.logger.warning("Can't connect to Solr" + url, exc_info=True)
                    print resp
                    print content
                except IndexingError:
                    self.logger.warning("Could not post " + filename + " Error: " + resp['status'], exc_info=True)
                    print resp
                    print content
                except Exception:
                    self.logger.warning("Could not complete post operation for " + filename, exc_info=True)
                    print resp
                    print content
                    
    def run(self, Params):
        '''
        Post Solr Input Documents to Solr core and perform index maintenance 
        operations.
        '''
        # get parameters
        actions = Params.get("post","actions").split(",")
        index = Params.get("post","index")
        source = Params.get("post","input")
        if Params.has_option("post", "required"):
            required = Params.get("post","required").split(',')
        else:
            required = []
        # execute actions
        for action in actions:
            if action == "flush":
                self.flush(index)
            # post
            elif action == "post":
                self.post(source,index,required)
            # commit
            elif action == "commit":
                self.commit(index)
            # optimize
            elif action == "optimize":
                self.optimize(index)
        