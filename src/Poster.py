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
        self.logger = logging.getLogger('Poster')

    def commit(self, solr, report=None, waitsearcher=False, waitflush=False):
        '''
        Commit staged data to the Solr core.
        '''
        # check state
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # send command
        msg = '<commit waitFlush="false" waitSearcher="false" expungeDeletes="true"/>'
        if solr.endswith('/'):
            url = solr + 'update'
        else:
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
        if solr.endswith('/'):
            url = solr + 'update'
        else:
            url = solr + '/update'
        (resp, content) = Http().request(url, "POST", msg)
        if resp['status'] != '200':
            print content
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
        if solr.endswith('/'):
            url = solr + 'update'
        else:
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
        if solr.endswith('/'):
            url = solr + 'update'
        else:
            url = solr + '/update'
        files = os.listdir(source)
        for filename in files:
            # read file
            infile = open(source + os.sep + filename, 'r')
            data = infile.read()
            infile.close()
            # remove xml declaration before posting to server
            data = data.replace("<?xml version='1.0' encoding='ASCII'?>",'')
            # post file
            try:
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
                    
    def run(self, params):
        '''
        Post Solr Input Documents to Solr core and perform index maintenance 
        operations.
        '''
        # get parameters
        actions = params.get("post","actions").split(",")
        index = params.get("post","index")
        report = params.get("post","report")
        source = params.get("post","input")
        # execute actions
        for action in actions:
            if action == "flush":
                self.flush(index,report)
            # post
            elif action == "post":
                self.post(source,index,report)
            # commit
            elif action == "commit":
                self.commit(index,report)
            # optimize
            elif action == "optimize":
                self.optimize(index,report)
        