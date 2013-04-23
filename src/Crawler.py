'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from DigitalObjectCache import DigitalObjectCache
from EacCpf import EacCpf
from HtmlPage import HtmlPage

import fnmatch
import logging
import os
import time
        
class Crawler(object):
    '''
    File system and web site crawler. Locates HTML files with embedded digital
    object representations, extracts their metadata and URL to related image 
    file. It stores metadata in an intermediary file, and digital objects in a 
    file system image cache.
    '''

    def __init__(self):
        '''
        Initialize the crawler.
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

    def _isUrl(self, Source):
        ''' 
        Determine if Source is a URL.
        '''
        if 'http://' in Source or 'https://' in Source:
            return True
        return False

    def _makeCache(self, Path):
        '''
        Create a cache folder at the specified path if none exists.
        If the path already exists, delete all files within it.
        '''
        if not os.path.exists(Path):
            os.makedirs(Path)
            self.logger.info("Created output folder at " + Path)
        else:
            self._clearFiles(Path)
            self.logger.info("Cleared output folder at " + Path)
    
    def crawlFileSystem(self, Source, Output, Report, Actions=['html'], Base=None, Sleep=0.):
        '''
        Crawl file system for HTML files. Execute the specified indexing 
        actions on each file. Store files to the Output path. Sleep for the 
        specified number of seconds after fetching data.
        '''
        # make sure that Base has a trailing /
        if not Base.endswith('/'):
            Base = Base + '/'
        # walk the file system and look for html files
        for path, _, files in os.walk(Source):
            # construct the public url for the file
            baseurl = Base + path.replace(Source,'')
            if not baseurl.endswith('/'):
                baseurl = baseurl + '/'
            self.logger.info('Current source ' + path + ' (' + baseurl + ')')
            # for each file in the current path
            for filename in files:
                if self._isHTML(filename):
                    self.logger.debug("Found document " + path + os.sep + filename)
                    try:
                        # if the page represents a record
                        html = HtmlPage(path + os.sep + filename, baseurl)
                        if html.hasRecord():
                            metadata = html.getEacCpfUrl()
                            presentation = html.getUrl()
                            if 'eaccpf' in Actions and html.hasEacCpfAlternate():
                                eaccpf = EacCpf(metadata,presentation)
                                eaccpf.write(Output)
                            if 'eaccpf-thumbnail' in Actions and html.hasEacCpfAlternate():
                                eaccpf = EacCpf(metadata,presentation)
                                thumbnail = eaccpf.getThumbnail()
                                if thumbnail:
                                    cacherecord = self.cache.put(thumbnail)
                                    dobj_id = eaccpf.getRecordId()
                                    thumbnail.write(Output,dobj_id,cacherecord)
                            if 'digitalobject' in Actions and html.hasEacCpfAlternate():
                                eaccpf = EacCpf(metadata,presentation)
                                dobjects = eaccpf.getDigitalObjects()
                                for dobject in dobjects:
                                    cacherecord = self.cache.put(dobject)
                                    dobject.write(Output,Cacherecord=cacherecord)
                            if 'html' in Actions:
                                html.write(Output)
                    except Exception:
                        self.logger.warning("Could not complete processing for " + filename)
                    finally:
                        time.sleep(Sleep)
    
    def crawlWebSite(self, source, output, report, actions=['html'], sleep=0.):
        '''
        Crawl web site for HTML entity pages. When such a page is found, 
        execute the specified indexing actions. Store files to the output path.
        Sleep for the specified number of seconds after fetching data.
        '''
        self.logger.warning("Web site crawling is not implemented")

    def run(self, Params):
        '''
        Execute crawl operation using specified parameters.
        '''
        # determine the type of crawl operation to be executed
        actions = Params.get("crawl","actions").split(",")
        base = Params.get("crawl","base")
        cache = Params.get("crawl","cache")
        cacheurl = Params.get("crawl","cache-url")
        source = Params.get("crawl","input")
        output = Params.get("crawl","output")
        report = Params.get("crawl","report")
        sleep = float(Params.get("crawl","sleep"))
        # digital object cache
        self.cache = DigitalObjectCache(cache,cacheurl)
        # create output folders
        self._makeCache(output)
        if not os.path.exists(report):
            os.makedirs(report)
        # check state before starting
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        assert os.path.exists(cache), self.logger.warning("Cache path does not exist: " + cache)
        assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # start processing
        if (self._isUrl(source)):
            self.crawlWebSite(source,output,report,actions,sleep)
        else:
            self.crawlFileSystem(source,output,report,actions,base,sleep)

