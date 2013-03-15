'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

import fnmatch
import logging
import os
import time
import yaml
from HtmlPage import HtmlPage
from ImageCache import ImageCache
        
class Crawler(object):
    '''
    File system and web site crawler. Locates HTML files with embedded DObject
    representations, extracts their metadata and URL to related image file.
    It stores the metadata in an intermediary file, and the image in a file 
    system image cache.
    '''

    def __init__(self):
        '''
        Initialize the crawler
        '''
        self.logger = logging.getLogger('Crawler')
    
    def _clearFiles(self, path):
        '''
        Delete all files within the specified path.
        '''
        files = os.listdir(path)
        for filename in files:
            os.remove(path + os.sep + filename)
    
    def _isHTML(self, filename):
        '''
        Determine if a file is an *.htm or *.html file.
        '''
        if fnmatch.fnmatch(filename,'*.html') or fnmatch.fnmatch(filename,'*.htm'):
            return True
        return False

    def _isUrl(self, uri):
        ''' 
        Determine if URI is a URL.
        '''
        if 'http://' in uri or 'https://' in uri:
            return True
        return False

    def _makeCache(self, Path):
        '''
        Create a cache folder at the specified path if none exists.
        If the path already exists, delete all files.
        '''
        if not os.path.exists(Path):
            os.makedirs(Path)
            self.logger.info("Created output folder at " + Path)
        else:
            self._clearFiles(Path)
            self.logger.info("Cleared output folder at " + Path)
    
    def crawlFileSystem(self, source, output, actions=['html'], base=None, report=None, sleep=0.):
        '''
        Crawl file system for HTML files. Execute the specified indexing 
        actions on files that contain or are related to an EAC-CPF record. 
        '''
        # check state
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # strip the trailing / from the base url
        if base.endswith('/'):
            base = base[:-1]
        # walk file system and look for html, htm files
        for path, _, files in os.walk(source):
            # construct the public url for the file
            url = base + path.replace(source,'')
            for filename in files:
                if self._isHTML(filename):
                    self.logger.debug("Found document " + path + os.sep + filename)
                    fileurl = url + '/' + filename
                    try:
                        html = HtmlPage(path + os.sep + filename, fileurl)
                        if html.getRecordId():
                            if 'eaccpf' in actions and html.hasEacCpfAlternate():
                                self.logger.debug("Storing EAC-CPF document " + filename)
                                # this should save the file to the local storage, not index it!
                                # self.indexEACCPF(html, output, report)
                            if 'digitalobject' in actions and html.hasDigitalObject():
                                self.storeDigitalObject(html, output, report)
                            if 'html' in actions:
                                html.write(output + os.sep + filename)
                    except Exception:
                        self.logger.warning("Could not complete processing for " + filename, exc_info=True)
                    finally:
                        time.sleep(sleep)
    
    def crawlWebSite(self, source, output, actions=['html'], report=None, sleep=0.):
        '''
        Crawl web site for HTML pages that have EAC-CPF alternate 
        representations.  When such a page is found, copy the referenced  
        data file to a local cache for processing. If no cache is specified, 
        it creates a local cache in the current working directory. Sleep
        for the specified number of seconds after fetching data.
        '''
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # crawl web site and look for html files

    def indexEACCPF(self, html, output, report):
        '''
        Index EAC-CPF content contained in the HTML document.
        '''
        pass
    
    def run(self, params):
        '''
        Execute crawl operation using specified parameters.
        '''
        # determine the type of crawl operation to be executed
        actions = params.get("crawl","actions")
        base = params.get("crawl","base")
        cache = params.get("crawl","cache")
        source = params.get("crawl","input")
        output = params.get("crawl","output")
        report = params.get("crawl","report")
        sleep = float(params.get("crawl","sleep"))
        # set image cache
        self.cache = ImageCache(cache)
        # create output folders
        self._makeCache(output)
        if not os.path.exists(report):
            os.makedirs(report)
        # start operation if source is specified
        if (self._isUrl(source)):
            self.crawlWebSite(source,output,report,sleep)
        else:
            self.crawlFileSystem(source,output,actions,base,report,sleep)

    def storeDigitalObject(self, html, output, report):
        '''
        Store the digital object contained in the referenced HTML file to an
        intermediate YML representation.
        '''
        dobj = html.getDigitalObject()
        recordId = html.getRecordId()
        dobj['id'] = recordId
        dobj['source'] = html.getUri()
        if dobj:
            # cache the object at the referenced url
            cache_id, cache_path = self.cache.store(dobj['url'])
            dobj['cache_id'] = cache_id
            dobj['cache_path'] = cache_path
        else:
            # append skeleton outfile_path and note about absence of dobj info
            pass
        # write metadata outfile_path to output
        outfile_path = output + os.sep + recordId + ".yml"
        outfile = open(outfile_path,'w')
        yaml.dump(dobj, outfile, default_flow_style=False, indent=4)
        outfile.close()
        self.logger.info("Stored digital object from " + html.getUri())
        
