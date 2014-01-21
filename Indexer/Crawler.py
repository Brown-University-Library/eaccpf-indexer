"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from DigitalObjectCache import DigitalObjectCache
from EacCpf import EacCpf
from HtmlPage import HtmlPage

import Cfg
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
        self.log = logging.getLogger()

    def crawlFileSystem(self, Source, Output, Actions, FileIndex, Base=None, Sleep=0.0, UpdateOnly=False):
        """
        Crawl file system for HTML files. Execute the specified indexing 
        actions on each file. Store files in the Output path. Sleep for the
        specified number of seconds after fetching data. The Update parameter
        controls whether we should process the file only if it has changed.
        """
        # list of records that have been discovered
        records = []
        # make sure that Base has a trailing /
        Base = "{}/".format(Base) if Base and not Base.endswith('/') else Base
        Source = "{}/".format(Source) if Source and not Source.endswith('/') else Source
        # walk the file system and look for html files
        for path, _, files in os.walk(Source):
            # construct an assumed public url for the file
            baseurl = Base + path.replace(Source, '')
            baseurl += '/' if not baseurl.endswith('/') else baseurl
            self.log.debug("Visiting {} ({})".format(path, baseurl))
            # for each file in the current path
            for filename in files:
                if filename.endswith(".htm") or filename.endswith(".html"):
                    self.log.debug("Scanning {}".format(filename))
                    try:
                        html = HtmlPage(path + os.sep + filename, baseurl)
                        if 'html-all' in Actions:
                            html.write(Output)
                        elif html.hasEacCpfAlternate():
                            self.log.debug("Entity document found at {0}".format(path + os.sep + filename))
                            if 'html' in Actions:
                                html.write(Output)
                                continue
                            # get the eaccpf document
                            metadata = html.getEacCpfUrl()
                            presentation = html.getUrl()
                            src = Source + metadata.replace(Base, '')
                            if not Utils.resourceExists(src):
                                self.log.warning("Resource not available {0}".format(src))
                                continue
                            eaccpf = EacCpf(src, metadata, presentation)
                            # we will check the eaccpf document to see if its changed
                            record_filename = eaccpf.getFileName()
                            records.append(record_filename)
                            fileHash = eaccpf.getHash()
                            # if the file has not changed since the last run then skip it
                            if UpdateOnly and record_filename in FileIndex and FileIndex[record_filename] == fileHash:
                                self.log.info("No change since last update {0}".format(record_filename))
                                continue
                            FileIndex[record_filename] = fileHash
                            if 'eaccpf' in Actions:
                                eaccpf.write(Output)
                            if 'eaccpf-thumbnail' in Actions:
                                try:
                                    thumbnail_record = eaccpf.getThumbnail()
                                    if thumbnail_record:
                                        self.log.debug("Thumbnail found for {0}".format(filename))
                                        cache_record = self.cache.put(thumbnail_record.getSourceUrl())
                                        eaccpf_id = eaccpf.getRecordId()
                                        thumbnail_record.write(Output, Id=eaccpf_id, CacheRecord=cache_record)
                                except:
                                    self.log.error("Could not write thumbnail for {0}".format(filename), exc_info=Cfg.LOG_EXC_INFO)
                            if 'digitalobject' in Actions:
                                dobjects = eaccpf.getDigitalObjects()
                                try:
                                    for dobject in dobjects:
                                        self.log.debug("Digital object found for {0}".format(filename))
                                        cache_record = self.cache.put(dobject.getSourceUrl())
                                        dobj_id = dobject.getObjectId()
                                        dobject.write(Output, Id=dobj_id, CacheRecord=cache_record)
                                except:
                                    self.log.error("Could not write digital object for {0}".format(filename), exc_info=Cfg.LOG_EXC_INFO)
                    except:
                        self.log.error("Could not complete processing for {0}".format(filename), exc_info=Cfg.LOG_EXC_INFO)
                    finally:
                        time.sleep(Sleep)
        # return the list of processed records
        return records

    def crawlWebSite(self, Source, Output, Actions, FileIndex, Sleep=0.0, UpdateOnly=False):
        """
        Crawl web site for HTML entity pages. When such a page is found, 
        execute the specified indexing actions. Store files to the output path.
        Sleep for the specified number of seconds after fetching data.
        """
        self.log.error("Web site crawling is not implemented")

    def run(self, Params, Update=False):
        """
        Execute crawl operation using specified parameters.
        """
        # parameters
        actions = Params.get("crawl", "actions").split(",")
        cache = Params.get("crawl", "cache")
        cacheUrl = Params.get("crawl", "cache-url")
        source = Params.get("crawl", "input")
        output = Params.get("crawl", "output")
        sleep = Params.getfloat("crawl", "sleep")
        # check state before starting
        assert os.path.exists(source), self.log.error("Input path does not exist: {0}".format(source))
        if not os.path.exists(output):
            os.makedirs(output)
        Utils.cleanOutputFolder(output, Update=Update)
        self.cache = DigitalObjectCache(cache, cacheUrl)
        assert os.path.exists(output), self.log.error("Output path does not exist: {0}".format(output))
        # create an index of file hashes, so that we can track what has changed
        hashIndex = {}
        if Update:
            hashIndex = Utils.loadFileHashIndex(output)
        # crawl the document source
        if 'http://' in source or 'https://' in source:
            records = self.crawlWebSite(source, output, actions, hashIndex, sleep, Update)
        else:
            base = Params.get("crawl", "base")
            records = self.crawlFileSystem(source, output, actions, hashIndex, base, sleep, Update)
        # remove records from the index that were deleted in the source
        if Update:
            self.log.info("Clearing orphaned records from the file hash index")
            Utils.purgeIndex(records, hashIndex)
        # remove files from the output folder that are not in the index
        if Update:
            self.log.info("Clearing orphaned files from the output folder")
            Utils.purgeFolder(output, hashIndex)
        # write the updated file index
        Utils.writeFileHashIndex(hashIndex, output)
