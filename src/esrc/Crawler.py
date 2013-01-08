'''
This file is subject to the terms and conditions defined in the
'LICENSE.txt' file, which is part of this source code package.
'''

from HTMLParser import HTMLParser
import fnmatch
import logging
import os
import time
import urllib2

class EACMetaRefParser(HTMLParser,object):
    '''
    Parser for extracting references to EAC alternate representations.
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        super(EACMetaRefParser,self).__init__()
        self.eac = None
        
    def getEacRef(self):
        '''
        '''
        return self.eac

    def handle_starttag(self, tag, attributes):
        '''
        If the tag is of type 'meta', contains a name value of 'EAC' or 
        'EAC-CPF' then return the value of the 'content' attribute.
        '''
        if tag != 'meta':
            return
        attr = dict(attributes)
        if attr.has_key('name'):
            if attr.get('name') == 'EAC' or attr.get('name') == 'EAC-CPF':
                if (attr.has_key('content')):
                    self.eac = attr.get('content')
        
class Crawler(object):
    '''
    File system and web site crawler. Locates EAC metadata files either 
    directly or when specified as an alternate representation to an HTML file. 
    Downloads a copy of the discovered files to a local file system cache for 
    future processing.
    '''

    def __init__(self):
        '''
        Initialize the crawler
        '''
        self.logger = logging.getLogger('feeder')
        self.parser = EACMetaRefParser()
    
    def _getFileName(self, url):
        '''
        Get the filename portion of a URL. If no filename is present within the 
        URL, return None. 
        '''
        last = (url.split('/')[-1])
        if (last):
            return last
        return None
    
    def _isHTML(self, filename):
        '''
        Determine if a file is an *.htm or *.html file.
        '''
        if fnmatch.fnmatch(filename,'*.html') or fnmatch.fnmatch(filename,'*.htm'):
            return True
        return False
    
    def _isUrl(self, uri):
        ''' 
        Determine if a URI is an URL.
        '''
        if 'http://' in uri:
            return True
        return False

    def _makeCache(self, path):
        '''
        Create a cache folder at the specified path if none exists.
        If the path already exists, delete all files.
        '''
        if not os.path.exists(path):
            os.makedirs(path)
            self.logger.info("Created output folder at " + path)
        else:
            files = os.listdir(path)
            for afile in files:
                os.remove(path + os.sep + afile)
            self.logger.info("Cleared output folder at " + path)
    
    def crawlFileSystem(self, root='.', output='output', report=None, sleep=0.):
        '''
        Crawl file system for HTML files, starting from the file root, and 
        looking for those files which have EAC, EAC-CPF alternate 
        representations. Mirror EAC eac files to the specified output. If no 
        output is specified, it creates a default local in the current working 
        directory. Sleep for the specified number of seconds after fetching 
        data.
        '''
        self.logger.info("Crawling file system from " + root)
        # create a output for our eac
        self._makeCache(output)
        # walk file system and look for html, htm files
        for path, _, files in os.walk(root):
            for filename in files:
                if self._isHTML(filename):
                    self.logger.debug("Found " + path + os.sep + filename)
                    try:
                        # if the file has an EAC alternate representation
                        html = open((path + os.sep + filename),'r').read()
                        self.parser.reset()
                        self.parser.feed(html)
                        url = self.parser.getEacRef() 
                        if url:
                            self.logger.debug("Found " + url)
                            # download the file
                            eac = urllib2.urlopen(url).read()
                            # write the file to the output
                            datafilename = self._getFileName(url)
                            if datafilename:
                                f = open((output + os.sep + datafilename),'w')
                                f.write(eac)
                                f.close()
                                self.logger.info("Stored " + url)
                    except Exception, e:
                        self.logger.critical("Could not complete processing for " + filename + "\n" + e)
                    finally:
                        time.sleep(sleep)
    
    def crawlWebSite(self, baseurl='http://localhost', cache='data', report=None, sleep=0.):
        '''
        Crawl web site for HTML pages that have EAC, EAC-CPF alternate 
        representations.  When such a page is found, copy the referenced EAC 
        data file to a local cache for processing. If no cache is specified, 
        it creates a default local in the current working directory. Sleep
        for the specified number of seconds after fetching data.
        '''
        self.logger.info("Crawling web site", baseurl)
        # create the cache if it does not exist
        self._makeCache(cache)
        # start crawling operation
        try:
            pass
        except Exception:
            self.logger.critical("Could not complete processing for")
        finally:
            time.sleep(sleep)
        
    def run(self, params):
        '''
        Execute crawl operation.
        '''
        self.logger.info("Starting crawl operation")
        # determine the type of crawl operation to be executed
        source = params.get("crawl","input")
        output = params.get("crawl","output")
        report = params.get("crawl","report")
        sleep = int(params.get("crawl","sleep"))
        # start operation if source is specified
        if (self._isUrl(source)):
            self.crawlWebSite(source,output,report,sleep)
        else:
            self.crawlFileSystem(source,output,report,sleep)
