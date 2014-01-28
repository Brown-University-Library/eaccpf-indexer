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

    def __init__(self, actions, base, cache, cache_url, source, output, sleep=1.0, update=False):
        self.cache = None
        self.hashIndex = {}
        self.log = logging.getLogger()
        self.records = [] # list of records that have been discovered
        # parameters
        self.actions = actions
        self.base = base if base else None
        self.cache = cache
        self.cacheUrl = cache_url
        self.source = source
        self.output = output
        self.sleep = sleep
        self.update = update
        # make sure that paths have a trailing /
        self.base = "{}/".format(self.base) if self.base and not self.base.endswith('/') else self.base
        self.source = "{}/".format(self.source) if self.source and not self.source.endswith('/') else self.source

    def crawlFileSystem(self):
        """
        Crawl file system for HTML files. Execute the specified indexing 
        actions on each file. Store files in the Output path. Sleep for the
        specified number of seconds after fetching data. The Update parameter
        controls whether we should process the file only if it has changed.
        """
        # walk the file system and look for html files
        for path, _, files in os.walk(self.source):
            # construct an assumed public url for the file
            base_url = self.base + path.replace(self.source, '')
            base_url += '/' if not base_url.endswith('/') else ''
            self.log.debug("Scanning {} ({})".format(path, base_url))
            # for each file in the current path
            for filename in [f for f in files if f.endswith("htm") or f.endswith("html")]:
                self.log.debug("Reading {}".format(filename))
                try:
                    html = HtmlPage(path, filename, base_url)
                    if 'html-all' in self.actions:
                        html.write(self.output)
                    elif html.hasEacCpfAlternate():
                        self.log.debug("Entity document found at {0}".format(path + os.sep + filename))
                        if 'html' in self.actions:
                            html.write(self.output)
                        else:
                            self.process_eaccpf(html)
                except:
                    self.log.error("Could not complete processing for {0}".format(filename), exc_info=Cfg.LOG_EXC_INFO)
                finally:
                    time.sleep(self.sleep)

    def crawlWebSite(self):
        """
        Crawl web site for HTML entity pages. When such a page is found, 
        execute the specified indexing actions. Store files to the output path.
        Sleep for the specified number of seconds after fetching data.
        """
        self.log.error("Web site crawling is not implemented")

    def process_eaccpf(self, html):
        """
        Execute processing actions on the EAC-CPF document.
        """
        # get the document
        html_filename = html.getFilename()
        metadata_url = html.getEacCpfUrl()
        presentation_url = html.getUrl()
        eaccpf_src = self.source + metadata_url.replace(self.base, '')
        if not Utils.resourceExists(eaccpf_src):
            self.log.warning("EAC-CPF resource not available at {0}".format(eaccpf_src))
            return
        eaccpf = EacCpf(eaccpf_src, metadata_url, presentation_url)
        # record the document hash value
        record_filename = eaccpf.getFileName()
        self.records.append(record_filename)
        file_hash = eaccpf.getHash()
        # if the file has not changed since the last run then skip it or is not
        # already present then record the new file hash
        if self.update and record_filename in self.hashIndex and self.hashIndex[record_filename] == file_hash:
            self.log.info("No change since last update {0}".format(record_filename))
            return
        self.hashIndex[record_filename] = file_hash
        self.log.debug("Added file hash {0} {1}".format(record_filename, file_hash))
        # execute processing actions
        if 'eaccpf' in self.actions:
            eaccpf.write(self.output)
        if 'eaccpf-thumbnail' in self.actions:
            try:
                thumbnail_record = eaccpf.getThumbnail()
                if thumbnail_record:
                    self.log.debug("Thumbnail found for {0}".format(html_filename))
                    cache_record = self.cache.put(thumbnail_record.getSourceUrl())
                    eaccpf_id = eaccpf.getRecordId()
                    thumbnail_record.write(self.output, Id=eaccpf_id, CacheRecord=cache_record)
            except:
                msg = "Could not write thumbnail for {0}".format(html_filename)
                self.log.error(msg, exc_info=Cfg.LOG_EXC_INFO)
        if 'digitalobject' in self.actions:
            try:
                dobjects = eaccpf.getDigitalObjects()
                for dobject in dobjects:
                    self.log.debug("Digital object found for {0}".format(html_filename))
                    cache_record = self.cache.put(dobject.getSourceUrl())
                    dobj_id = dobject.getObjectId()
                    dobject.write(self.output, Id=dobj_id, CacheRecord=cache_record)
            except:
                msg = "Could not write digital object for {0}".format(html_filename)
                self.log.error(msg, exc_info=Cfg.LOG_EXC_INFO)

    def run(self):
        """
        Execute crawl operation.
        """
        # check state before starting
        assert os.path.exists(self.source), self.log.error("Input path does not exist: {0}".format(self.source))
        if not os.path.exists(self.output):
            os.makedirs(self.output)
        Utils.cleanOutputFolder(self.output, Update=self.update)
        assert os.path.exists(self.output), self.log.error("Output path does not exist: {0}".format(self.output))
        # digital object cache
        self.cache = DigitalObjectCache(self.cache, self.cacheUrl)
        # create an index of file hashes so that we can track which files have
        # changed
        self.records = []
        if self.update:
            self.hashIndex = Utils.loadFileHashIndex(self.output)
        # crawl the document source
        if 'http://' in self.source or 'https://' in self.source:
            self.crawlWebSite()
        else:
            self.crawlFileSystem()
        # remove records from the index that were deleted in the source
        if self.update:
            self.log.info("Clearing orphaned records from the file hash index")
            Utils.purgeIndex(self.records, self.hashIndex)
        # remove files from the output folder that are not in the index
        if self.update:
            self.log.info("Clearing orphaned files from the output folder")
            Utils.purgeFolder(self.output, self.hashIndex)
        # write the updated file index
        Utils.writeFileHashIndex(self.hashIndex, self.output)


def crawl(params, update):
    """
    Execute crawl operations using the specified parameters.
    """
    actions = params.get("crawl", "actions").split(",")
    base = params.get("crawl","base") if params.has_option("crawl","base") else ''
    cache = params.get("crawl", "cache")
    cache_url = params.get("crawl", "cache-url")
    source = params.get("crawl", "input")
    output = params.get("crawl", "output")
    sleep = params.getfloat("crawl", "sleep")
    # execute
    crawler = Crawler(actions, base,  cache, cache_url, source, output, sleep, update)
    crawler.run()
