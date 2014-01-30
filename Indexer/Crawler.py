"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from DigitalObjectCache import DigitalObjectCache
from EacCpf import EacCpf
from HtmlPage import HtmlPage

import Cfg
import Timer
import Utils
import fnmatch
import logging
import os


class Crawler(object):
    """
    File system and web site crawler. Locates HTML files with embedded digital
    object representations, extracts their metadata and URL to related image 
    file. It stores metadata in an intermediary file, and digital objects in a 
    file system image cache.
    """

    def __init__(self, actions, base, source, output, cache=None, exclude=None, sleep=1.0, update=False):
        self.hashIndex = {}
        self.log = logging.getLogger()
        self.records = [] # list of records that have been discovered
        # parameters
        self.actions = actions
        self.base = base if base else None
        self.cache = cache
        self.exclude = exclude if exclude else []
        self.output = output
        self.sleep = sleep
        self.source = source
        self.update = update
        # make sure that paths have a trailing /
        self.base = "{}/".format(self.base) if self.base and not self.base.endswith('/') else self.base
        self.source = "{}/".format(self.source) if self.source and not self.source.endswith('/') else self.source

    def _excluded(self, filename):
        """
        Return True if the file should be excluded based on whether it matches
        a pattern specified as part of the exclude list. Return false
        otherwise.
        """
        for pattern in self.exclude:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False

    def crawlFileSystem(self):
        """
        Crawl file system for HTML files. Execute the specified indexing 
        actions on each file. Store files in the Output path. Sleep for the
        specified number of seconds after fetching data. The Update parameter
        controls whether we should process the file only if it has changed.
        """
        for path, _, files in os.walk(self.source):
            # construct an assumed public url for the path
            base_url = self.base + path.replace(self.source, '')
            base_url += '/' if not base_url.endswith('/') else ''
            # scan the current path
            self.log.debug("Scanning {} ({})".format(path, base_url))
            for filename in [f for f in files if f.endswith(".htm") or f.endswith(".html")]:
                self.log.debug("Reading {}".format(filename))
                try:
                    html = HtmlPage(path, filename, base_url)
                    if 'html-all' in self.actions:
                        self.process_html(html)
                    elif 'html' in self.actions and html.hasEacCpfAlternate():
                        self.process_html(html)
                    elif html.hasEacCpfAlternate():
                        self.process_eaccpf(html)
                except:
                    self.log.error("Could not complete processing for {0}".format(filename), exc_info=Cfg.LOG_EXC_INFO)

    def crawlWebSite(self):
        """
        Crawl web site for HTML entity pages. When such a page is found, 
        execute the specified indexing actions. Store files to the output path.
        Sleep for the specified number of seconds after fetching data.
        """
        self.log.error("Web site crawling is not implemented")

    def process_eaccpf(self, html):
        """
        Execute processing actions on the EAC-CPF document that is referenced
        inside the presentation HTML document.
        """
        html_filename = html.getFilename()
        metadata_url = html.getEacCpfUrl()
        presentation_url = html.getUrl()
        eaccpf_src = self.source + metadata_url.replace(self.base, '')
        if not Utils.resourceExists(eaccpf_src):
            self.log.warning("EAC-CPF resource not available at {0}".format(eaccpf_src))
            return
        eaccpf = EacCpf(eaccpf_src, metadata_url, presentation_url)
        # if the document file name is in the exclude list, then don't process it
        record_filename = eaccpf.getFileName()
        if self._excluded(record_filename):
            return
        # record the document hash value
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

    def process_html(self, html):
        """
        Store the HTML page content in the output folder.
        """
        if self._excluded(html.filename):
            return
        self.records.append(html.filename)
        # if the file has not changed since the last run then skip it
        file_hash = Utils.getFileHash(html.source)
        if self.update and html.filename in self.hashIndex and self.hashIndex[html.filename] == file_hash:
            self.log.info("No change since last update {0}".format(html.filename))
            return
        # record the new or updated file hash
        self.hashIndex[html.filename] = file_hash
        # store the document in the output folder
        html.write(self.output)

    def run(self):
        """
        Execute crawl operation.
        """
        with Timer.Timer() as t:
            # check state before starting
            assert os.path.exists(self.source), self.log.error("Input path does not exist: {0}".format(self.source))
            if not os.path.exists(self.output):
                os.makedirs(self.output)
            Utils.cleanOutputFolder(self.output, Update=self.update)
            assert os.path.exists(self.output), self.log.error("Output path does not exist: {0}".format(self.output))
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
        # log execution time
        self.log.info("Crawler finished in {0}:{1}:{2}".format(t.hours, t.minutes, t.seconds))

def crawl(params, update):
    """
    Execute crawl operations using the specified parameters.
    """
    actions = params.get("crawl", "actions").split(",")
    base = params.get("crawl", "base") if params.has_option("crawl", "base") else ''
    exclude = params.get("crawl","exclude").split(',') if params.has_option("crawl","exclude") else []
    source = params.get("crawl", "input")
    output = params.get("crawl", "output")
    sleep = params.getfloat("crawl", "sleep") if params.has_option("crawl","sleep") else 0.0
    # if we need a digital object cache, then get the configuration values
    # from the config file, create the cache object and pass it to the crawler
    if 'eaccpf' in actions:
        cache_path = params.get("crawl", "cache") if params.has_option("crawl", "cache") else ''
        cache_url = params.get("crawl", "cache-url") if params.has_option("crawl", "cache-url") else ''
        cache = DigitalObjectCache(cache_path, cache_url)
    else:
        cache = None
    # execute
    crawler = Crawler(actions, base, source, output, cache=cache, sleep=sleep, exclude=exclude, update=update)
    crawler.run()

