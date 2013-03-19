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
        If the path already exists, delete all files within it.
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
        actions on each file. Store files to the output path. Sleep for the 
        specified number of seconds after fetching data.
        '''
        # add a trailing / to the base url if it doesn't exist
        if not base.endswith('/'):
            base = base + '/'
        # walk file system and look for html, htm files
        for path, _, files in os.walk(source):
            # construct the public url for the file
            baseurl = base + path.replace(source,'')
            if '//' in baseurl:
                baseurl = baseurl.replace('//','/')
            # for each file in the current path
            for filename in files:
                if self._isHTML(filename):
                    self.logger.debug("Found document " + path + os.sep + filename)
                    try:
                        html = HtmlPage(path + os.sep + filename, baseurl)
                        # if the page represents an entity
                        if html.getRecordId():
                            if 'eaccpf' in actions and html.hasEacCpfAlternate():
                                data, filename = html.getEACCPF()
                                # append source and referrer values in comment
                                src = html._getEacCpfReference()
                                ref = html.getUrl()
                                data += '\n<!-- @source=%(source)s @referrer=%(referrer)s -->' % {"source":src, "referrer":ref}
                                self.store(output, filename, data, report)
                            if 'digitalobject' in actions and html.hasDigitalObject():
                                data, filename = self.getDigitalObjectRecord(html)
                                self.store(output, filename, data, report)
                            if 'html' in actions:
                                data = html.getContent()
                                self.store(output, filename, data, report)
                    except Exception:
                        self.logger.warning("Could not complete processing for " + filename, exc_info=True)
                    finally:
                        time.sleep(sleep)
    
    def crawlWebSite(self, source, output, actions=['html'], report=None, sleep=0.):
        '''
        Crawl web site for HTML entity pages. When such a page is found, 
        execute the specified indexing actions. Store files to the output path.
        Sleep for the specified number of seconds after fetching data.
        '''
        self.logger.warning("Web site crawling is not implemented")

    def getDigitalObjectRecord(self, html, output, report):
        '''
        Transform the metadata contained in the HTML page to an intermediate 
        YML digital object representation.
        '''
        dobj = html.getDigitalObjectRecord()
        recordId = html.getRecordId()
        dobj['id'] = recordId
        dobj['source'] = html.getUrl()
        if dobj:
            # cache the object at the referenced url
            cache_id, cache_path = self.cache.store(dobj['url'])
            dobj['cache_id'] = cache_id
            dobj['cache_path'] = cache_path
        else:
            # append skeleton outfile_path and note about absence of dobj info
            pass
        # write data to output
        filename = recordId + ".yml"
        data = yaml.dump(dobj, default_flow_style=False, indent=4)
        # return
        return data, filename
        
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
        # check state before starting
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        assert os.path.exists(cache), self.logger.warning("Cache path does not exist: " + cache)
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # start operation if source is specified
        if (self._isUrl(source)):
            self.crawlWebSite(source,output,report,sleep)
        else:
            self.crawlFileSystem(source,output,actions,base,report,sleep)

    def store(self, output, filename, data, report):
        '''
        Store data to file in output folder.
        '''
        outfile_path = output + os.sep + filename
        outfile = open(outfile_path,'w')
        outfile.write(data)
        outfile.close()
        self.logger.info("Stored document " + filename)

        
