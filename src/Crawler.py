'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from DigitalObjectCache import DigitalObjectCache
from EacCpf import EacCpf
from HtmlPage import HtmlPage

import logging
import os
import shutil
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
        self.cache = None
        self.logger = logging.getLogger('Crawler')

    def _makeCache(self, Path):
        '''
        Create a cache folder at the specified path if none exists.
        If the path already exists, delete all files within it.
        '''
        if os.path.exists(Path):
            shutil.rmtree(Path)
        os.makedirs(Path)
        self.logger.info("Cleared output folder at " + Path)

    def crawlFileSystem(self, Source, Output, Actions, Base=None, Sleep=0.):
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
                if filename.endswith(".htm") or filename.endswith(".html"):
                    self.logger.debug("Found document " + path + os.sep + filename)
                    try:
                        # if the page represents a record
                        html = HtmlPage(path + os.sep + filename, baseurl)
                        if html.hasRecord():
                            metadata = html.getEacCpfUrl()
                            presentation = html.getUrl()
                            src = Source + html.getEacCpfUrl().replace(Base,'')
                            if 'eaccpf' in Actions and html.hasEacCpfAlternate():
                                eaccpf = EacCpf(src,metadata,presentation)
                                eaccpf.write(Output)
                            if 'eaccpf-thumbnail' in Actions and html.hasEacCpfAlternate():
                                eaccpf = EacCpf(src,metadata,presentation)
                                thumbnail = eaccpf.getThumbnail()
                                if thumbnail:
                                    cacherecord = self.cache.put(thumbnail)
                                    dobj_id = eaccpf.getRecordId()
                                    thumbnail.write(Output,dobj_id,cacherecord)
                            if 'digitalobject' in Actions and html.hasEacCpfAlternate():
                                eaccpf = EacCpf(src,metadata,presentation)
                                dobjects = eaccpf.getDigitalObjects()
                                for dobject in dobjects:
                                    cacherecord = self.cache.put(dobject)
                                    dobject.write(Output,Cacherecord=cacherecord)
                            if 'html' in Actions:
                                html.write(Output)
                    except:
                        self.logger.warning("Could not complete processing for " + filename, exc_info=True)
                    finally:
                        time.sleep(Sleep)

    def crawlWebSite(self, Source, Output, Actions, Sleep=0.):
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
        try:
            sleep = Params.getfloat("crawl","sleep")
        except:
            sleep = 0.0
        # digital object cache
        self.cache = DigitalObjectCache(cache,cacheurl)
        # create output folders
        self._makeCache(output)
        # check state before starting
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        assert os.path.exists(cache), self.logger.warning("Cache path does not exist: " + cache)
        # start processing
        if 'http://' in source or 'https://' in source:
            self.crawlWebSite(source,output,actions,sleep)
        else:
            self.crawlFileSystem(source,output,actions,base,sleep)
