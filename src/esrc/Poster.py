'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from httplib2 import Http
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
        self.logger = logging.getLogger('feeder')

    def commit(self, solr, report=None, waitsearcher=False, waitflush=False):
        '''
        Commit staged data to the Solr core.
        '''
        # check state
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # send command
        msg = '<commit waitFlush="false" waitSearcher="false" expungeDeletes="true"/>'
        url = solr + '/update'
        (resp, content) = Http().request(url, "POST", msg)
        if resp['status'] != '200':
            raise IndexingError(resp, content)
        self.logger.info("Commited staged data to " + solr)
        return resp, content

            
    def flush(self, solr, report=None):
        """
        Flush all documents from Solr.
        """
        # check state
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # send command
        msg = "<delete><query>*</query></delete>"
        url = solr + '/update'
        (resp, content) = Http().request(url, "POST", msg)
        if resp['status'] != '200':
            raise IndexingError(resp, content)
        self.logger.info("Flushed data from " + solr)
        return (resp, content)
        
    def optimize(self, solr, report=None, waitsearcher=False):
        '''
        Optimize data in Solr core.
        '''
        # check state
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # send command
        msg = '<optimize waitSearcher="false"/>'
        url = solr + '/update'
        (resp, content) = Http().request(url, "POST", msg)
        if resp['status'] != '200':
            raise IndexingError(resp, content)
        self.logger.info("Optimized " + solr)
        return (resp, content)
        
    def post(self, source, solr, report=None):
        '''
        Post Solr Input Documents to Solr core.
        '''
        # check state
        assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # post documents
        url = solr + '/update'
        files = os.listdir(source)
        for filename in files:
            # read file
            infile = open(source + os.sep + filename, 'r')
            data = infile.read()
            infile.close()
            # remove xml declaration
            data = data.replace("<?xml version='1.0' encoding='ASCII'?>",'')
            # post file
            try:
                (resp, content) = Http().request(url, "POST", data)
                if resp['status'] != '200':
                    raise IndexingError(resp, content)
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
                    
    def run(self, params):
        '''
        Post Solr Input Documents to Solr core and perform index maintenance 
        operations.
        '''
        # get parameters
        source = params.get("post","input")
        report = params.get("post","report")
        post = params.get("post","post")
        flush = params.get("post","flush")
        commit = params.get("post","commit")
        optimize = params.get("post","optimize")
        index = params.get("post","index")
        # delete
        if flush.lower() == "true":
            self.flush(index,report)
        # post
        if post.lower() == "true":
            self.post(source,index,report)
        # commit
        if commit.lower() == "true":
            self.commit(index,report)
        # optimize
        if optimize.lower() == "true":
            self.optimize(index,report)
        