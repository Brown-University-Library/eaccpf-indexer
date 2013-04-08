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
import yaml
        
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
    
    def _write(self, Path, Filename, Data):
        '''
        Write data to the file in the specified path.
        '''
        outfile_path = Path + os.sep + Filename
        outfile = open(outfile_path,'w')
        outfile.write(Data)
        outfile.close()
        self.logger.info("Stored document " + Filename)
        
    def crawlFileSystem(self, Source, Output, Actions=['html'], Base=None, Report=None, Sleep=0.):
        '''
        Crawl file system for HTML files. Execute the specified indexing 
        actions on each file. Store files to the Output path. Sleep for the 
        specified number of seconds after fetching data.
        '''
        # add a trailing / to the Base url if it doesn't exist
        if not Base.endswith('/'):
            Base = Base + '/'
        # walk file system and look for html, htm files
        for path, _, files in os.walk(Source):
            # construct the public url for the file
            if path.startswith('/'):
                baseurl = Base + path.replace(Source,'')[1:]
            else:
                baseurl = Base + path.replace(Source,'')
            self.logger.info('Current path is ' + baseurl)
            # for each file in the current path
            for filename in files:
                if self._isHTML(filename):
                    self.logger.debug("Found document " + path + os.sep + filename)
                    try:
                        html = HtmlPage(path + os.sep + filename, baseurl)
                        # if the page represents a record
                        if html.getRecordId():
                            if 'eaccpf' in Actions and html.hasEacCpfAlternate():
                                src = html.getEacCpfUrl()
                                ref = html.getUrl()
                                eaccpf = EacCpf(src)
                                data = eaccpf.data
                                # append source and referrer values in comment
                                data += '\n<!-- @Source=%(Source)s @referrer=%(referrer)s -->' % {"Source":src, "referrer":ref}
                                self._write(Output, eaccpf.getFileName(), data)
                            if 'digitalobject' in Actions and html.hasEacCpfAlternate():
                                url = html.getEacCpfUrl()
                                eaccpf = EacCpf(url)
                                dobjects = eaccpf.getDigitalObjects()
                                if len(dobjects) > 0:
                                    for dobject in dobjects:
                                        # cache the object at the referenced url
                                        src = dobject['dobj_url']
                                        cached = self.cache.put(src)
                                        for key in cached.keys():
                                            dobject[key] = cached[key]
                                        # write data to output
                                        filename = dobject['id'] + ".yml"
                                        data = yaml.dump(dobject, default_flow_style=False, indent=4)
                                        self._write(Output, filename, data)
                            if 'html' in Actions:
                                data = html.getContent()
                                self._write(Output, filename, data)
                    except Exception:
                        self.logger.warning("Could not complete processing for " + filename, exc_info=True)
                    finally:
                        time.sleep(Sleep)
    
    def crawlWebSite(self, source, output, actions=['html'], report=None, sleep=0.):
        '''
        Crawl web site for HTML entity pages. When such a page is found, 
        execute the specified indexing actions. Store files to the output path.
        Sleep for the specified number of seconds after fetching data.
        '''
        self.logger.warning("Web site crawling is not implemented")
        
    def run(self, params):
        '''
        Execute crawl operation using specified parameters.
        '''
        # determine the type of crawl operation to be executed
        actions = params.get("crawl","actions").split(",")
        base = params.get("crawl","base")
        cache = params.get("crawl","cache")
        cacheurl = params.get("crawl","cache-url")
        source = params.get("crawl","input")
        output = params.get("crawl","output")
        report = params.get("crawl","report")
        sleep = float(params.get("crawl","sleep"))
        # digital object cache
        self.cache = DigitalObjectCache(cache,cacheurl)
        # create output folders
        self._makeCache(output)
        if not os.path.exists(report):
            os.makedirs(report)
        # check state before starting
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        assert os.path.exists(cache), self.logger.warning("Cache path does not exist: " + cache)
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # start processing
        if (self._isUrl(source)):
            self.crawlWebSite(source,output,report,sleep)
        else:
            self.crawlFileSystem(source,output,actions,base,report,sleep)

