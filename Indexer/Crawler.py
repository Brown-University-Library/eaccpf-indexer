"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from DigitalObjectCache import DigitalObjectCache
from EacCpf import EacCpf
from HtmlPage import HtmlPage
import Utils
import logging
import os
import time


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
        self.hashIndexFilename = ".index.yml"
        self.logger = logging.getLogger('Crawler')

    def crawlFileSystem(self, Source, Output, Actions, HashIndex, Base=None, Sleep=0.0, UpdateOnly=False):
        """
        Crawl file system for HTML files. Execute the specified indexing 
        actions on each file. Store files to the Output path. Sleep for the 
        specified number of seconds after fetching data. The Update parameter
        controls whether we should process the file only if it has changed.
        """
        # list of records that have been discovered
        records = []
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
                    try:
                        # if the page represents a record
                        html = HtmlPage(path + os.sep + filename, baseurl)
                        if html.hasEacCpfAlternate():
                            self.logger.debug("Record found at " + path + os.sep + filename)
                            # get the eaccpf document
                            metadata = html.getEacCpfUrl()
                            presentation = html.getUrl()
                            src = Source + html.getEacCpfUrl().replace(Base, '')
                            eaccpf = EacCpf(src, metadata, presentation)
                            # we will check the eaccpf document to see if its changed
                            record_filename = eaccpf.getFileName()
                            records.append(record_filename)
                            fileHash = eaccpf.getHash()
                            # if the file has not changed since the last run then skip it
                            if UpdateOnly:
                                if record_filename in HashIndex and HashIndex[record_filename] == fileHash:
                                    self.logger.info("No change since last update " + record_filename)
                                    continue
                            HashIndex[record_filename] = fileHash
                            if 'eaccpf' in Actions:
                                eaccpf.write(Output)
                            if 'eaccpf-thumbnail' in Actions:
                                thumbnail = eaccpf.getThumbnail()
                                if thumbnail:
                                    cacherecord = self.cache.put(thumbnail)
                                    dobj_id = eaccpf.getRecordId()
                                    thumbnail.write(Output, dobj_id, cacherecord)
                            if 'digitalobject' in Actions:
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
        # return the list of processed records
        return records

    def crawlWebSite(self, Source, Output, Actions, HashIndex, Sleep=0.0, UpdateOnly=False):
        """
        Crawl web site for HTML entity pages. When such a page is found, 
        execute the specified indexing actions. Store files to the output path.
        Sleep for the specified number of seconds after fetching data.
        """
        self.logger.warning("Web site crawling is not implemented")
        return []

    def run(self, Params, Update=False):
        """
        Execute crawl operation using specified parameters.
        """
        # parameters
        actions = Params.get("crawl", "actions").split(",")
        base = Params.get("crawl", "base")
        cache = Params.get("crawl", "cache")
        cacheUrl = Params.get("crawl", "cache-url")
        source = Params.get("crawl", "input")
        output = Params.get("crawl", "output")
        sleep = Params.getfloat("crawl", "sleep")
        # clear output folder and cache
        if not Update:
            Utils.cleanOutputFolder(output)
        self.cache = DigitalObjectCache(cache, cacheUrl)
        # check state before starting
        assert os.path.exists(source), self.logger.warning("Input path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        assert os.path.exists(cache), self.logger.warning("Cache path does not exist: " + cache)
        # create an index of file hashes, so that we can track what has changed
        hashIndex = {}
        if Update:
            hashIndex = Utils.loadFileHashIndex(output)
        # crawl the document source
        if 'http://' in source or 'https://' in source:
            records = self.crawlWebSite(source, output, actions, hashIndex, sleep, Update)
        else:
            records = self.crawlFileSystem(source, output, actions, hashIndex, base, sleep, Update)
        # remove records from the index that were deleted in the source
        if Update:
            self.logger.info("Clearing orphaned records from the file hash index")
            Utils.purgeIndex(records, hashIndex)
        # remove files from the output folder that are not in the index
        if Update:
            self.logger.info("Clearing orphaned files from the output folder")
            Utils.purgeFolder(output, hashIndex)
        # write the updated file hash index
        Utils.writeFileHashIndex(hashIndex, output)
