"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from EacCpf import EacCpf
from HtmlPage import HtmlPage
from DigitalObjectCache import DigitalObjectCache
import logging
import os
import shutil
import time
import yaml


class Crawler(object):
    """
    File system and web site crawler. Locates HTML files with embedded digital
    object representations, extracts their metadata and URL to related image 
    file. It stores metadata in an intermediary file, and digital objects in a 
    file system image cache.
    """

    def __init__(self):
        """
        Initialize the crawler.
        """
        self.cache = None
        self.logger = logging.getLogger('Crawler')

    def _clearOutput(self, Path):
        """
        Create a cache folder at the specified path if none exists.
        If the path already exists, delete all files within it.
        """
        if os.path.exists(Path):
            shutil.rmtree(Path)
        os.makedirs(Path)
        self.logger.info("Cleared output folder at " + Path)

    def _loadFileIndex(self, Path):
        """
        Load the file index from the specified path and return a dictionary
        with the filename as the key and hash as the value.
        """
        if os.path.exists(Path + os.sep + "index.yml"):
            infile = open(Path + os.sep + 'index.yml','r')
            data = infile.read()
            index = yaml.load(data)
            infile.close()
            return index
        else:
            return {}

    def _writeFileIndex(self, Data, Path):
        """
        Write the file hash index to the specified path.
        """
        outfile = open(Path + os.sep + 'index.yml','w')
        yaml.dump(Data,outfile)
        outfile.close()

    def crawlFileSystem(self, Source, Output, Actions, Base=None, Sleep=0., UpdateOnly=False):
        """
        Crawl file system for HTML files. Execute the specified indexing 
        actions on each file. Store files to the Output path. Sleep for the 
        specified number of seconds after fetching data. The Update parameter
        controls whether we should process the file only if it has changed.
        """
        # load file hash index
        index = self._loadFileIndex(Output)
        if index == None:
            index = {}
        # make sure that Base has a trailing /
        if not Base.endswith('/'):
            Base += '/'
            # walk the file system and look for html files
        for path, _, files in os.walk(Source):
            # construct the public url for the file
            baseurl = Base + path.replace(Source, '')
            if not baseurl.endswith('/'):
                baseurl += '/'
            self.logger.info('Current source ' + path + ' (' + baseurl + ')')
            # for each file in the current path
            for filename in files:
                if filename.endswith(".htm") or filename.endswith(".html"):
                    self.logger.debug("Found document " + path + os.sep + filename)
                    try:
                        # if the page represents a record
                        html = HtmlPage(path + os.sep + filename, baseurl)
                        if html.hasRecord():
                            # check to see if the file has changed since the last run
                            # if it has, update the file hash record and continue processing
                            if UpdateOnly:
                                fileHash = html.getHash()
                                if not filename in index or index[filename] != fileHash:
                                    index[filename] = fileHash
                                else:
                                    break
                            metadata = html.getEacCpfUrl()
                            presentation = html.getUrl()
                            src = Source + html.getEacCpfUrl().replace(Base, '')
                            if 'eaccpf' in Actions and html.hasEacCpfAlternate():
                                eaccpf = EacCpf(src, metadata, presentation)
                                eaccpf.write(Output)
                            if 'eaccpf-thumbnail' in Actions and html.hasEacCpfAlternate():
                                eaccpf = EacCpf(src, metadata, presentation)
                                thumbnail = eaccpf.getThumbnail()
                                if thumbnail:
                                    cacherecord = self.cache.put(thumbnail)
                                    dobj_id = eaccpf.getRecordId()
                                    thumbnail.write(Output, dobj_id, cacherecord)  # @todo FAILING HERE!!!
                            if 'digitalobject' in Actions and html.hasEacCpfAlternate():
                                eaccpf = EacCpf(src, metadata, presentation)
                                dobjects = eaccpf.getDigitalObjects()
                                for dobject in dobjects:
                                    cacherecord = self.cache.put(dobject)
                                    dobject.write(Output, CacheRecord=cacherecord)
                            if 'html' in Actions:
                                html.write(Output)
                    except:
                        self.logger.warning("Could not complete processing for " + filename, exc_info=True)
                    finally:
                        time.sleep(Sleep)
        # write the updated index file
        self._writeFileIndex(index, Output)

    def crawlWebSite(self, Source, Output, Actions, Sleep=0.0, UpdateOnly=False):
        """
        Crawl web site for HTML entity pages. When such a page is found, 
        execute the specified indexing actions. Store files to the output path.
        Sleep for the specified number of seconds after fetching data.
        """
        self.logger.warning("Web site crawling is not implemented")

    def run(self, Params, UpdateOnly=False):
        """
        Execute crawl operation using specified parameters.
        """
        # determine the type of crawl operation to be executed
        actions = Params.get("crawl", "actions").split(",")
        base = Params.get("crawl", "base")
        cache = Params.get("crawl", "cache")
        cacheurl = Params.get("crawl", "cache-url")
        source = Params.get("crawl", "input")
        output = Params.get("crawl", "output")
        try:
            sleep = Params.getfloat("crawl", "sleep")
        except:
            sleep = 0.0
            # digital object cache
        self.cache = DigitalObjectCache(cache, cacheurl)
        # create output folders
        if not UpdateOnly:
            self._clearOutput(output)
        # check state before starting
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        assert os.path.exists(cache), self.logger.warning("Cache path does not exist: " + cache)
        # start processing
        if 'http://' in source or 'https://' in source:
            self.crawlWebSite(source, output, actions, sleep, UpdateOnly)
        else:
            self.crawlFileSystem(source, output, actions, base, sleep, UpdateOnly)
