'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from httplib2 import Http
from lxml import etree
import sys

class IndexingError(Exception):
    def __init__(self, resp, content):
        self.status = "Server response status: " + resp['status']
        self.content = content

    def __str__(self):
        return repr(self.status)
        return repr(self.content)

class Index(object):
    '''
    Abstraction of the Solr interface.
    '''

    def __init__(self, update_url):
        self.update_url = update_url

    def commit(self):
        """Commit the pending updates"""
        msg = '<commit waitFlush="false" waitSearcher="false" expungeDeletes="true"/>'
        #(resp, content) = Http().request(self.update_url, "POST", msg)
        return Http().request(self.update_url, "POST", msg)

    def clean(self):
        """Delete all documents that don't have the current version"""
        msg = "<delete><query>*</query></delete>"
        #(resp, content) = Http().request(self.update_url, "POST", msg)
        return Http().request(self.update_url, "POST", msg)

    def optimize(self):
        """Optimize the on disk index"""
        msg = '<optimize waitSearcher="false"/>'
        #(resp, content) = Http().request(self.update_url, "POST", msg)
        return Http().request(self.update_url, "POST", msg)

    def submit(self, doc, document, doctype, show):
        # then submit them to solr for indexing
        try:
            # this bit is very important:
            #  the document needs to be converted to a string before sending it to solr
            (resp, content) = Http().request(self.update_url, "POST", etree.tostring(doc))
            if resp['status'] != '200':
                raise IndexingError(resp, content)
        except IOError:
            print "Unable to open" + self.update_url + "in order to index the document. Check Solr"
            sys.exit(-1)
        except IndexingError as i: 
            print document + " not indexed. doctype: " + doctype + " HTML error: " + resp['status']
            if show:
                print i.status
                print i.content
