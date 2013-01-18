'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from httplib2 import Http
from lxml import etree
import logging
import os 
import urllib
import urllib2

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
        # commit
        msg = '<commit waitFlush="false" waitSearcher="false" expungeDeletes="true"/>'
        url = solr + '/update'
        (resp, content) = Http().request(url, "POST", msg)
        self.logger.info("Committed data to Solr core " + solr)
        #commit_xml = etree.Element('commit')
        #commit_xml.set('waitFlush', str(waitflush))
        #commit_xml.set('waitSearcher', str(waitsearcher))
        #url = solr + '/update'
        #request = urllib2.Request(url)
        #request.add_header('Content-Type', 'text/xml; charset=utf-8')
        #request.add_data(etree.tostring(commit_xml, pretty_print=True))
        #response = urllib2.urlopen(request).read()
        #status = etree.XML(response).findtext('lst/int')
        #return url, status
            
    def flush(self, solr, report=None):
        """
        Flush all documents from Solr.
        """
        # check state
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # flush data
        params = {}
        params['commit'] = 'true'
        url = solr + '/update?' + urllib.urlencode(params)
        request = urllib2.Request(url)
        request.add_header('Content-Type', 'text/xml; charset=utf-8')
        request.add_data('<delete><query>*:*</query></delete>')
        response = urllib2.urlopen(request).read()
        status = etree.XML(response).findtext('lst/int')
        return url, status
        
    def optimize(self, solr, report=None, waitsearcher=False):
        '''
        Optimize data in Solr core.
        '''
        # check state
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # optimize
        msg = '<optimize waitSearcher="false"/>'
        try:
            (resp, content) = Http().request(solr, "POST", msg)
            if resp['status'] != '200':
                raise IndexingError(resp, content)
            self.logger.info("Optimized data in " + solr)
        except Exception:
            self.logger.critical("Optimize operation failed", exc_info=True)
        
    def post(self, source, solr, report=None):
        '''
        Post Solr Input Documents to Solr core.
        '''
        # check state
        assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # get file list
        files = os.listdir(source)
        for filename in files:
            # read file
            infile = open(source + os.sep + filename, 'r')
            data = infile.read()
            infile.close()
            # post file
            try:
#                url = solr + '/update'
#                print url
#                request = urllib2.Request(url)
#                request.add_header('Content-Type', 'text/xml; charset=utf-8')
#                request.add_data(data)
#                response = urllib2.urlopen(request).read()
#                status = etree.XML(response).findtext('lst/int')
#                return url, status
#            except Exception:
#                self.logger.warning("Could not post " + filename, exc_info=True)
                (resp, content) = Http().request(solr, "POST", data)
                if resp['status'] != '200':
                    raise IndexingError(resp, content)        
                self.logger.info("Posted data from " + filename)
            except IOError:
                self.logger.warning("Can't connect to " + solr)
            except Exception:
                self.logger.warning("Could not post" + filename, exc_info=True) 
    
    def update(self, solr, docs, commitwithin=None):
        """
        Post list of docs to Solr, return URL and status. Option to tell Solr 
        to "commit within" that many milliseconds.
        """
        url = self.url + '/update'
        add_xml = etree.Element('add')
        if commitwithin is not None:
            add_xml.set('commitWithin', str(commitwithin))
        for doc in docs:
            xdoc = etree.SubElement(add_xml, 'doc')
            for key, value in doc.iteritems():
                if value:
                    field = etree.Element('field', name=key)
                    field.text = (value if isinstance(value, unicode)
                                  else str(value))
                    xdoc.append(field)
        request = urllib2.Request(url)
        request.add_header('Content-Type', 'text/xml; charset=utf-8')
        request.add_data(etree.tostring(add_xml, pretty_print=True))
        response = urllib2.urlopen(request).read()
        status = etree.XML(response).findtext('lst/int')
        return url, status
    
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
        