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
    Crawls a file system for target files and stores them in a local file
    system cache when found.

    base value
    ----------

    Crawled content is principally intended for viewing and presentation on the
    web. Each content item requires a public URL. The base value is used as an
    aid to the Crawler, to help it infer the public URL for any given file in
    the file system and represents the public URL that corresponds with the
    input folder. For example:

        base=http://www.example.com
        input=/path/to/data

    Here, the public URL that corresponds with the input folder is
    'http://www.example.com'. If the Crawler then enters the path,
    '/path/to/data/subfolder', the public URL of that folder would then be
    'http://www.example.com/subfolder'.

    Crawling with --update
    ----------------------

    The update option controls whether the Crawler should clear the cache then
    process all source files, or keep the existing cache and only process those
    files that have changed since the last run. To track whether a file has
    changed, we store its name and hash. When processing updates, we then
    locate each target document, record its name as having been processed, then
    compare its current hash value against the prior hash value recorded in the
    prior crawl operation. If the file name/hash value is not present in our
    index, or the hash has changed since the last run, then we know that the
    file is either new or updated and should be processed. At the end of the
    crawl operation, we then have a) a list of files that we have processed,
    and b) an index of files and their respective hashes.

    Files that have been added to the source should have been identified and
    should now be present in the crawl cache. Files that have been deleted in
    the source are now still present in the crawl cache. We first purge our
    index of files that are not in our list of processed files, then purge the
    cache of any files not present in our index. The cache should now reflect
    the contents of the source.

    Digital Objects
    ---------------

    Two files may be produced

    EAC-CPF: E000012.xml
    Thumbnail metadata: E000012.yml
    Digital Object record: AD0000012.yml


    """

    def __init__(self, actions, base, source, output, cache_path, cache_url, exclude=None, sleep=1.0, update=False):
        self.hashIndex = {}
        self.log = logging.getLogger()
        self.records = [] # list of records that have been discovered
        # parameters
        self.actions = actions
        self.base = base if base else None
        self.cache = DigitalObjectCache(cache_path, cache_url)
        self.exclude = exclude if exclude else []
        self.output = output
        self.sleep = sleep
        self.source = source
        self.update = update
        # make sure that paths have a trailing /
        self.base = "{}/".format(self.base) if self.base and not self.base.endswith('/') else self.base
        self.source = "{}/".format(self.source) if self.source and not self.source.endswith('/') else self.source

    def _is_excluded(self, filename):
        """
        Return True if the file should be excluded based on whether it matches
        a pattern specified as part of the exclude list. Return False
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
            self.log.debug("Scanning {0} ({1})".format(path, base_url))
            for filename in [f for f in files if f.endswith(".htm") or f.endswith(".html")]:
                self.log.debug("Reading {0}".format(filename))
                try:
                    html = HtmlPage(path, filename, base_url)
                    if 'html-all' in self.actions:
                        self.process_html(html)
                    elif 'html-entity' in self.actions and html.hasEacCpfAlternate():
                        self.process_html(html)
                    elif 'html' in self.actions and html.hasEacCpfAlternate():
                        # this action is for backward compatibility.
                        # 'html-entity' is more descriptive and should be used
                        # instead
                        self.process_html(html)
                    elif html.hasEacCpfAlternate():
                        metadata_url = html.getEacCpfUrl()
                        presentation_url = html.getUrl()
                        eaccpf_path = self.source + metadata_url.replace(self.base, '')
                        if not os.path.exists(eaccpf_path):
                            self.log.warning("EAC-CPF resource not available at {0}".format(eaccpf_path))
                        else:
                            eaccpf = EacCpf(eaccpf_path, metadata_url, presentation_url)
                            if 'eaccpf' in self.actions:
                                self.process_eaccpf(eaccpf)
                            if 'eaccpf-thumbnail' in self.actions:
                                self.process_eaccpf_thumbnail(eaccpf)
                            if 'eaccpf-digitalobject' in self.actions:
                                self.process_eaccpf_digital_objects(eaccpf)
                            if 'digitalobject' in self.actions:
                                # this action is for backward compatibility.
                                # 'eaccpf-digitalobject' is more descriptive
                                # and should be used instead
                                self.process_eaccpf_digital_objects(eaccpf)
                except:
                    self.log.error("Could not complete processing for {0}".format(filename), exc_info=Cfg.LOG_EXC_INFO)

    def crawlWebSite(self):
        """
        Crawl web site for HTML entity pages. When such a page is found, 
        execute the specified indexing actions. Store files to the output path.
        Sleep for the specified number of seconds after fetching data.
        """
        self.log.error("Web site crawling is not implemented")

    def process_eaccpf(self, doc):
        """
        Execute crawl actions on the EAC-CPF document.
        """
        # if the document file name is in the exclude list, then don't process it
        record_filename = doc.getFileName()
        if self._is_excluded(record_filename):
            self.log.debug("Document excluded {0}".format(record_filename))
            return
        # add the document file name to the list of documents that exist in the
        # source and have been processed
        self.records.append(record_filename)
        file_hash = doc.getHash()
        # if the file has not changed since the last run then skip it
        if self.update and record_filename in self.hashIndex and self.hashIndex[record_filename] == file_hash:
            self.log.debug("EAC-CPF has not changed since last update")
            return
        else:
            # store the file
            self.log.debug("EAC-CPF is new or changed since last run")
            doc.write(self.output)
            # record the document hash so that we can track whether its changed
            # on the next processing run
            self.hashIndex[record_filename] = file_hash

    def process_eaccpf_digital_objects(self, doc):
        """
        Execute crawl actions on EAC-CPF digital objects.
        """
        for dobj in doc.getDigitalObjects():
            self.log.debug("Found digital object record")
            try:
                dobj_id = dobj.getObjectId()
                dobj_path = dobj.getSourceUrl()
                # if the source object file name or metadata file name is in
                # the exclude list, then don't process it
                object_filename = Utils.getFileName(dobj_path)
                metadata_filename = dobj_id + ".yml"
                if self._is_excluded(object_filename) or self._is_excluded(metadata_filename):
                    self.log.debug("Digital object excluded {0}".format(dobj_id))
                    return
                # add the digital object metadata file name to the list of
                # documents that have been processed
                self.records.append(metadata_filename)
                record_hash = dobj.getHash()
                # if the file has not changed since the last run then skip it
                if self.update and metadata_filename in self.hashIndex and self.hashIndex[metadata_filename] == record_hash:
                    self.log.debug("Digital object has not changed since last update")
                    continue
                else:
                    self.log.debug("Digital object is new or changed since last run")
                    # put the source object in the digital object cache
                    # the identifier for the cache record must match the key
                    # used in the hashIndex below
                    cache_record = self.cache.put(metadata_filename, dobj_path)
                    # store the digital object metadata in the cache
                    dobj.write(self.output, Filename=metadata_filename, Id=dobj_id, CacheRecord=cache_record)
                    # record the metadata hash so that we can track whether its
                    # changed on the next processing run
                    self.hashIndex[metadata_filename] = record_hash
            except:
                msg = "Could not write digital object {0}".format(doc.getFileName())
                self.log.error(msg, exc_info=Cfg.LOG_EXC_INFO)

    def process_eaccpf_thumbnail(self, doc):
        """
        Execute crawl actions on EAC-CPF thumbnails.
        """
        dobj = doc.getThumbnail()
        if dobj:
            self.log.debug("Found thumbnail record")
            try:
                eaccpf_id = doc.getRecordId()
                dobj_id = dobj.getObjectId()
                dobj_path = dobj.getSourceUrl()
                # if the source object file name or metadata file name is in
                # the exclude list, then don't process it
                object_filename = Utils.getFileName(dobj_path)
                metadata_filename = eaccpf_id + ".yml"
                if self._is_excluded(object_filename) or self._is_excluded(metadata_filename):
                    self.log.debug("Thumbnail excluded {0}".format(dobj_id))
                    return
                # add the digital object metadata file name to the list of
                # documents that have been processed
                self.records.append(metadata_filename)
                record_hash = dobj.getHash()
                # if the file has not changed since the last run then skip it
                if self.update and metadata_filename in self.hashIndex and self.hashIndex[metadata_filename] == record_hash:
                    self.log.debug("Thumbnail has not changed since last update")
                    return
                else:
                    self.log.debug("Thumbnail is new or changed since last run")
                    # put the source object in the digital object cache
                    # the identifier for the cache record must match the key
                    # used in the hashIndex below
                    cache_record = self.cache.put(metadata_filename, dobj_path)
                    # store the digital object metadata in the cache
                    dobj.write(self.output, Filename=metadata_filename, Id=eaccpf_id, CacheRecord=cache_record)
                    # record the metadata hash so that we can track whether its
                    # changed on the next processing run
                    self.hashIndex[metadata_filename] = record_hash
            except:
                msg = "Could not write thumbnail for {0}".format(doc.getFileName())
                self.log.error(msg, exc_info=Cfg.LOG_EXC_INFO)

    def process_html(self, html):
        """
        Store the HTML page content in the output folder.
        """
        if self._is_excluded(html.filename):
            return
        self.records.append(html.filename)
        # if the file has not changed since the last run then skip it
        file_hash = Utils.getFileHash(html.source)
        if self.update and html.filename in self.hashIndex and self.hashIndex[html.filename] == file_hash:
            self.log.debug("HTML has not changed since last update {0}".format(html.filename))
            return
        else:
            self.log.debug("HTML is new or changed since last run")
            # store the document in the output folder
            html.write(self.output)
            # record the new or updated file hash
            self.hashIndex[html.filename] = file_hash

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
            # create an index of file hashes so that we can track which files
            # have changed since the last run
            self.records = []
            if self.update:
                self.hashIndex = Utils.loadFileHashIndex(self.output)
            # crawl the document source
            if 'http://' in self.source or 'https://' in self.source:
                self.crawlWebSite()
            else:
                self.crawlFileSystem()
            # if the crawl was executed as an update, then synchronize the file
            # index, metadata cache, and image cache folders with the source
            if self.update:
                # remove records from the index that were deleted in the source
                self.log.info("Clearing orphaned records from the file hash index")
                Utils.purgeIndex(self.records, self.hashIndex)
                # remove files from the metadata cache that are not in the index
                self.log.info("Clearing orphaned files from the output folder")
                Utils.purgeFolder(self.output, self.hashIndex)
                # remove files from the image cache that are not in the index
                self.log.info("Clearing orphaned files from the image cache")
                self.cache.purge(self.hashIndex.keys())
            # write the updated file index
            Utils.writeFileHashIndex(self.hashIndex, self.output)
        # log execution time
        self.log.info("Crawler finished in {0}:{1}:{2}".format(t.hours, t.minutes, t.seconds))

def crawl(params, update):
    """
    Execute crawl operations using the specified parameters.
    """
    # required configuration values
    actions = params.get("crawl", "actions").split(",")
    source = params.get("crawl", "input")
    output = params.get("crawl", "output")
    # optional configuration values
    base = params.get("crawl", "base") if params.has_option("crawl", "base") else ''
    exclude = params.get("crawl","exclude").split(',') if params.has_option("crawl","exclude") else []
    sleep = params.getfloat("crawl", "sleep") if params.has_option("crawl","sleep") else 0.0
    cache_url = params.get("crawl", "cache-url") if params.has_option("crawl", "cache-url") else '/'
    cache_path = params.get("crawl", "cache") if params.has_option("crawl", "cache") else ''
    # create the crawler then start processing
    crawler = Crawler(actions, base, source, output, cache_path=cache_path, cache_url=cache_url, sleep=sleep, exclude=exclude, update=update)
    crawler.run()
