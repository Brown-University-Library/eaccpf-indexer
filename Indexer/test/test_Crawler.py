"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from Indexer import Cfg
from Indexer import Crawler
from Indexer import Utils

import inspect
import logging
import os
import shutil
import tempfile
import unittest


class TestCrawler(unittest.TestCase):
    """
    Test cases for the Crawler module.
    """
    
    def setUp(self):
        """
        Setup the test environment.
        """
        self.cache = tempfile.mkdtemp()
        self.module = os.path.abspath(inspect.getfile(self.__class__))
        self.module_path = os.path.dirname(self.module)
        self.source = self.module_path + os.sep + "crawl"
        self.temp = tempfile.mkdtemp()

    def tearDown(self):
        """
        Tear down the test environment.
        """
        shutil.rmtree(self.temp, ignore_errors=True)
        shutil.rmtree(self.cache, ignore_errors=True)

    def test__init__(self):
        """
        It should create a crawler instance.
        """
        source = self.source + os.sep + "update_original"
        cases = [
            (['eaccpf'], 'http://www.example.com', self.cache, "http://www.example.com/cache", source, self.temp),
            ([], 'http://www.example.com', self.cache, "http://www.example.com/cache", source, self.temp),
        ]
        for case in cases:
            actions, base, cache_path, cache_url, source, output = case
            try:
                crawler = Crawler.Crawler(actions, base, source, output, cache_path, cache_url)
            except:
                logging.error("Could not create Crawler instance", exc_info=True)
                self.fail("Could not create Crawler instance")

    def test__excluded(self):
        """
        It should return True when the filename matches a specified exclude
        filename pattern. It should return False otherwise.
        """
        cases = [
            (['browse_(.*).htm'],'browse_a.htm', True),
            (['browse_(.*).htm'],'browse.htm', False),
            (['browse_(.*).htm','browse.htm'],'browse.htm', True),
            (['browse_(.*).htm','browse.htm'],'browser.htm', False),
        ]
        for case in cases:
            actions = []
            base = '/'
            source = self.temp
            output = self.temp
            cache_url = '/'
            excluded, filename, expected = case
            crawler = Crawler.Crawler(actions, base, source, output, self.cache, cache_url, exclude=excluded)
            result = crawler._is_excluded(filename)
            self.assertNotEqual(None, result)
            self.assertEqual(expected, result)

    def test_crawl_eaccpf(self):
        """
        It should retrieve files that exist. For each EAC-CPF file, it should
        add the metadata and presentation URLs as attributes to the eac-cpf
        node.
        """
        source = self.source + os.sep + "update_original"
        cases = [
            (['eaccpf'], 'http://www.findandconnect.gov.au', "http://www.findandconnect.gov.au/cache", source, self.temp, 3),
        ]
        for case in cases:
            actions, base, cache_url, source, output, expected_count = case
            try:
                crawler = Crawler.Crawler(actions, base, source, output, self.cache, cache_url)
                crawler.run()
            except:
                logging.error("Could not complete crawl job", exc_info=True)
                self.fail("Could not complete crawl job")
            # the output folder should have the same number of eac-cpf files as the source
            result_count = 0
            for filename in [f for f in os.listdir(output) if f.endswith(".xml")]:
                result_count += 1
            self.assertEqual(expected_count, result_count)
            # the file hash index should be present in the output folder
            path = output + os.sep + Cfg.HASH_INDEX_FILENAME
            self.assertEqual(True, os.path.exists(path))
            # the number of entries in the index should be the same as the file count
            hash_index = Utils.loadFileHashIndex(output)
            self.assertEqual(expected_count, len(hash_index))
            # the image cache folder should exist
            self.assertEqual(True, os.path.exists(self.cache))

    def test_crawl_eaccpf_digitalobjects(self):
        """
        It should crawl a source folder, locate all EAC-CPF documents, extract
        all digital object metadata, then store that metadata in the cache.
        When new EAC-CPF documents are added to the source, it should locate
        the new files then add all new digital object records into the cache.
        """
        actions = ['eaccpf-digitalobject']
        base = 'http://www.findandconnect.gov.au'
        cache = self.cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_original = self.source + os.sep + "update_original"
        expected_count = 1
        # crawl the source_original folder to establish the baseline
        crawler = Crawler.Crawler(actions, base, source_original, output, cache, cache_url)
        crawler.run()
        # the output folder should now contain a yaml file for each digital
        # object
        result_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".yml") and not f == Cfg.HASH_INDEX_FILENAME]:
            result_count += 1
        self.assertEqual(expected_count, result_count)
        # the hash index should now contain an entry for each digital object
        hash_index = Utils.loadFileHashIndex(output)
        self.assertEqual(expected_count, len(hash_index))
        # the image cache should now contain a folder for each digital object
        dobjs = crawler.cache.get_all()
        self.assertEqual(expected_count, len(dobjs))

    def test_crawl_eaccpf_digitalobjects_then_update_additions(self):
        """
        It should crawl a source folder for digital objects documents, then
        update the contents of the crawl and image caches with any newly
        added files on the second pass.
        """
        actions = ['eaccpf-digitalobject']
        base = 'http://www.findandconnect.gov.au'
        cache = self.cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_add = self.source + os.sep + "update_add"
        source_original = self.source + os.sep + "update_original"
        expected_file_count = 2
        # crawl the source folder to establish the baseline
        crawler = Crawler.Crawler(actions, base, source_original, output, cache, cache_url)
        crawler.run()
        # count the number of output files
        source_file_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".yml") and not f == Cfg.HASH_INDEX_FILENAME]:
            source_file_count += 1
        # crawl the source_add folder to process the changes
        crawler = Crawler.Crawler(actions, base, source_add, output, cache, cache_url, update=True)
        crawler.run()
        # the output folder should now contain a yaml file for each digital
        # object
        updated_file_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".yml") and not f == Cfg.HASH_INDEX_FILENAME]:
            updated_file_count += 1
        self.assertEqual(expected_file_count, updated_file_count)
        # the hash index should now contain an entry for each digital object
        hash_index = Utils.loadFileHashIndex(output)
        self.assertEqual(expected_file_count, len(hash_index))
        # the image cache should now contain a folder for each digital object
        dobjs = crawler.cache.get_all()
        self.assertEqual(expected_file_count, len(dobjs))

    def test_crawl_eaccpf_digitalobjects_then_update_changed(self):
        """
        It should crawl a source folder for digital objects, then update the
        contents of the crawl and image caches with any updated files on the
        second pass.
        """
        actions = ['eaccpf-digitalobject']
        base = 'http://www.findandconnect.gov.au'
        cache = self.cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_change = self.source + os.sep + "update_change"
        source_original = self.source + os.sep + "update_original"
        expected_file_count = 1
        # crawl the source_original folder to establish the baseline
        crawler = Crawler.Crawler(actions, base, source_original, output, cache, cache_url)
        crawler.run()
        # record the output file count and index file hash
        original_file_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".yml") and not f == Cfg.HASH_INDEX_FILENAME]:
            original_file_count += 1
        original_index_file_hash = Utils.getFileHash(self.temp + os.sep + Cfg.HASH_INDEX_FILENAME)
        # crawl for changes
        crawler = Crawler.Crawler(actions, base, source_change, output, cache, cache_url, update=True)
        crawler.run()
        # we should have the expected number of digital objects in the cache
        updated_file_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".yml") and not f == Cfg.HASH_INDEX_FILENAME]:
            updated_file_count += 1
        self.assertEqual(expected_file_count, updated_file_count)
        # the hash of the file index should have changed
        updated_index_file_hash = Utils.getFileHash(self.temp + os.sep + Cfg.HASH_INDEX_FILENAME)
        self.assertNotEqual(updated_index_file_hash, original_index_file_hash)
        # the image cache should contain a folder for each digital object
        dobjs = crawler.cache.get_all()
        self.assertEqual(expected_file_count, len(dobjs))

    def test_crawl_eaccpf_digitalobjects_then_update_deleted(self):
        """
        It should crawl a source folder for digital objects, then update the
        contents of the crawl and image caches with any deleted files on the
        second pass.
        """
        actions = ['eaccpf-digitalobject']
        base = 'http://www.findandconnect.gov.au'
        cache = self.cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_delete = self.source + os.sep + "update_delete"
        source_original = self.source + os.sep + "update_original"
        expected_file_count = 0
        # crawl the source_original folder to establish the baseline
        crawler = Crawler.Crawler(actions, base, source_original, output, cache, cache_url)
        crawler.run()
        # record the output file count and index file hash
        original_file_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".yml") and not f == Cfg.HASH_INDEX_FILENAME]:
            original_file_count += 1
        original_index_file_hash = Utils.getFileHash(self.temp + os.sep + Cfg.HASH_INDEX_FILENAME)
        # crawl for changes
        crawler = Crawler.Crawler(actions, base, source_delete, output, cache, cache_url, update=True)
        crawler.run()
        # we should have the expected number of digital objects in the cache
        updated_file_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".yml") and not f == Cfg.HASH_INDEX_FILENAME]:
            updated_file_count += 1
        self.assertEqual(expected_file_count, updated_file_count)
        # the hash of the file index should have changed
        updated_index_file_hash = Utils.getFileHash(self.temp + os.sep + Cfg.HASH_INDEX_FILENAME)
        self.assertNotEqual(updated_index_file_hash, original_index_file_hash)
        # the image cache should now contain a folder for each digital object
        dobjs = crawler.cache.get_all()
        self.assertEqual(expected_file_count, len(dobjs))

    def test_crawl_eaccpf_then_update_additions(self):
        """
        It should index a source folder and create an index of the stored
        files. When a subsequent index is executed, it should add any new
        files into the output folder and update the file index.
        """
        actions = ['eaccpf']
        base = 'http://www.findandconnect.gov.au'
        cache = self.cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_add = self.source + os.sep + "update_add"
        source_original = self.source + os.sep + "update_original"
        expected_count = 5
        # crawl the source_original folder to establish the baseline
        crawler = Crawler.Crawler(actions, base, source_original, output, cache, cache_url)
        crawler.run()
        # crawl the source_add folder to process the changes
        crawler = Crawler.Crawler(actions, base, source_add, output, cache, cache_url, update=True)
        crawler.run()
        # the output folder should now contain four eac-cpf documents
        result_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".xml")]:
            result_count += 1
        self.assertEqual(expected_count, result_count)
        # the hash index should now contain four records
        hash_index = Utils.loadFileHashIndex(output)
        self.assertEqual(expected_count, len(hash_index))

    def test_crawl_eaccpf_then_update_changed(self):
        """
        It should index a source
        """
        actions = ['eaccpf']
        base = 'http://www.findandconnect.gov.au'
        cache = self.cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_changed = self.source + os.sep + "update_change"
        source_original = self.source + os.sep + "update_original"
        # crawl the source_original folder to establish the baseline
        crawler = Crawler.Crawler(actions, base, source_original, output, cache, cache_url)
        crawler.run()
        # record the output file count and index file hash
        original_file_count = len(os.listdir(output))
        original_index_hash = Utils.getFileHash(output + os.sep + Cfg.HASH_INDEX_FILENAME)
        # crawl the source_add folder to process the changes
        crawler = Crawler.Crawler(actions, base, source_changed, output, cache, cache_url, update=True)
        crawler.run()
        # the output file count should be equal to the new output file count
        updated_file_count = len(os.listdir(output))
        self.assertEqual(original_file_count, updated_file_count)
        # the updated index file hash should be different from the original
        # output file index
        updated_index_hash = Utils.getFileHash(output + os.sep + Cfg.HASH_INDEX_FILENAME)
        self.assertNotEqual(original_index_hash, updated_index_hash)

    def test_crawl_eaccpf_then_update_deleted(self):
        """
        It should index a source folder and create an index of the stored
        files. When a subsequent index is executed, it should delete any
        files that have been removed from the source, update the output
        folder and file index.
        """
        actions = ['eaccpf']
        base = 'http://www.findandconnect.gov.au'
        cache = self.cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_delete = self.source + os.sep + "update_delete"
        source_original = self.source + os.sep + "update_original"
        expected_count = 2
        # crawl the source_original folder to establish the baseline
        crawler = Crawler.Crawler(actions, base, source_original, output, cache, cache_url)
        crawler.run()
        # crawl the source_add folder to process the changes
        crawler = Crawler.Crawler(actions, base, source_delete, output, cache, cache_url, update=True)
        crawler.run()
        # the output folder should now contain four eac-cpf documents
        result_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".xml")]:
            result_count += 1
        self.assertEqual(expected_count, result_count)
        # the hash index should now contain four records
        hash_index = Utils.loadFileHashIndex(output)
        self.assertEqual(expected_count, len(hash_index))

    def test_crawl_eaccpf_thumbnail(self):
        """
        It should crawl a source folder, locate all EAC-CPF documents, extract
        a thumbnail for each record, then store the thumbnail metadata in the
        cache.
        """
        actions = ['eaccpf-digitalobject']
        base = 'http://www.findandconnect.gov.au'
        cache = self.cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_original = self.source + os.sep + "update_original"
        expected_count = 1
        # crawl the source folder
        crawler = Crawler.Crawler(actions, base, source_original, output, cache, cache_url)
        crawler.run()
        # the output folder should now contain a yaml file for each thumbnail
        result_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".yml") and not f == Cfg.HASH_INDEX_FILENAME]:
            result_count += 1
        self.assertEqual(expected_count, result_count)
        # the hash index should now contain an entry for each digital object
        hash_index = Utils.loadFileHashIndex(output)
        self.assertEqual(expected_count, len(hash_index))
        # the image cache should now contain a folder for each digital object
        dobjs = crawler.cache.get_all()
        self.assertEqual(expected_count, len(dobjs))

    def test_crawl_eaccpf_thumbnail_then_update_additions(self):
        """
        It should crawl a source folder for digital objects documents, then
        update the contents of the crawl and image caches with any newly
        added files on the second pass.
        """
        actions = ['eaccpf-thumbnail']
        base = 'http://www.findandconnect.gov.au'
        cache = self.cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_add = self.source + os.sep + "update_add"
        source_original = self.source + os.sep + "update_original"
        expected_file_count = 2
        # crawl the source folder
        crawler = Crawler.Crawler(actions, base, source_original, output, cache, cache_url)
        crawler.run()
        # count the number of output files
        source_file_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".yml") and not f == Cfg.HASH_INDEX_FILENAME]:
            source_file_count += 1
        # crawl the update folder
        crawler = Crawler.Crawler(actions, base, source_add, output, cache, cache_url, update=True)
        crawler.run()
        # the output folder should now contain a yaml file for each digital
        # object
        updated_file_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".yml") and not f == Cfg.HASH_INDEX_FILENAME]:
            updated_file_count += 1
        self.assertEqual(expected_file_count, updated_file_count)
        # the hash index should now contain an entry for each digital object
        hash_index = Utils.loadFileHashIndex(output)
        self.assertEqual(expected_file_count, len(hash_index))
        # the image cache should now contain a folder for each digital object
        dobjs = crawler.cache.get_all()
        self.assertEqual(expected_file_count, len(dobjs))

    def test_crawl_eaccpf_thumbnail_then_update_changed(self):
        """
        It should crawl a source folder for thumbnails, then update the
        contents of the crawl and image caches with any updated files on the
        second pass.
        """
        actions = ['eaccpf-thumbnail']
        base = 'http://www.findandconnect.gov.au'
        cache = self.cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_change = self.source + os.sep + "update_change"
        source_original = self.source + os.sep + "update_original"
        expected_file_count = 1
        # crawl the source_original folder to establish the baseline
        crawler = Crawler.Crawler(actions, base, source_original, output, cache, cache_url)
        crawler.run()
        # record the output file count and index file hash
        original_file_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".yml") and not f == Cfg.HASH_INDEX_FILENAME]:
            original_file_count += 1
        original_index_file_hash = Utils.getFileHash(self.temp + os.sep + Cfg.HASH_INDEX_FILENAME)
        # crawl for changes
        crawler = Crawler.Crawler(actions, base, source_change, output, cache, cache_url, update=True)
        crawler.run()
        # we should have the expected number of digital objects in the cache
        updated_file_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".yml") and not f == Cfg.HASH_INDEX_FILENAME]:
            updated_file_count += 1
        self.assertEqual(expected_file_count, updated_file_count)
        # the hash of the file index should have changed
        updated_index_file_hash = Utils.getFileHash(self.temp + os.sep + Cfg.HASH_INDEX_FILENAME)
        self.assertNotEqual(updated_index_file_hash, original_index_file_hash)
        # the image cache should contain a folder for each digital object
        dobjs = crawler.cache.get_all()
        self.assertEqual(expected_file_count, len(dobjs))

    def test_crawl_eaccpf_thumbnail_then_update_deletions(self):
        """
        It should index a source folder and create an index of the stored
        files. When a subsequent index is executed, it should delete any
        files that have been removed from the source, update the output
        folder and file index.
        """
        actions = ['eaccpf-thumbnail']
        base = 'http://www.findandconnect.gov.au'
        cache = self.cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_delete = self.source + os.sep + "update_delete"
        source_original = self.source + os.sep + "update_original"
        expected_file_count = 0
        # crawl the source_original folder to establish the baseline
        crawler = Crawler.Crawler(actions, base, source_original, output, cache, cache_url)
        crawler.run()
        # crawl the source_add folder to process the changes
        crawler = Crawler.Crawler(actions, base, source_delete, output, cache, cache_url, update=True)
        crawler.run()
        # the output folder should now contain four eac-cpf documents and ????
        result_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".xml")]:
            result_count += 1
        self.assertEqual(expected_file_count, result_count)
        # the hash index should contain the expected number of records
        hash_index = Utils.loadFileHashIndex(output)
        self.assertEqual(expected_file_count, len(hash_index))
        # the image cache should now contain the expected file count
        dobjs = crawler.cache.get_all()
        self.assertEqual(expected_file_count, len(dobjs))

    def test_crawl_eaccpf_with_update_on_first_run(self):
        """
        When the crawler is invoked to index a new site for the first time and
        it given the --update option, it should add all discovered content to the
        cache in the first pass.
        """
        actions = ['eaccpf']
        base = 'http://www.findandconnect.gov.au'
        cache = self.cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_original = self.source + os.sep + "update_original"
        expected_count = 3
        # crawl the source_original folder to establish the baseline
        crawler = Crawler.Crawler(actions, base, source_original, output, cache, cache_url, update=True)
        crawler.run()
        # the cache folder should have content in it now
        result_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".xml")]:
            result_count += 1
        self.assertEqual(expected_count, result_count)

    def test_crawl_html(self):
        """
        It should crawl all HTML documents in the source folder that represent
        entities.
        """
        source = self.module_path + os.sep + "test_site"
        cases = [
            (['html'], 'http://www.findandconnect.gov.au', self.cache, "http://www.findandconnect.gov.au/cache", source, self.temp, 33),
        ]
        for case in cases:
            actions, base, cache, cache_url, source, output, expected_count = case
            try:
                crawler = Crawler.Crawler(actions, base, source, output, cache, cache_url)
                crawler.run()
            except:
                logging.error("Could not complete crawl job", exc_info=True)
                self.fail("Could not complete crawl job")
            # count the number of files in the output folder
            result_count = 0
            for filename in [f for f in os.listdir(output) if f.endswith(".htm") or f.endswith(".html")]:
                result_count += 1
            self.assertEqual(expected_count, result_count)
            # the file hash index should be present in the output folder
            path = output + os.sep + Cfg.HASH_INDEX_FILENAME
            self.assertEqual(True, os.path.exists(path))
            # the number of entries in the index should be the same as the file count
            hash_index = Utils.loadFileHashIndex(output)
            self.assertEqual(expected_count, len(hash_index))
            # the image cache folder should exist
            self.assertEqual(True, os.path.exists(self.cache))

    def test_crawl_html_all(self):
        """
        It should crawl all HTML documents in the source folder.
        """
        source = self.module_path + os.sep + "test_site"
        cases = [
            (['html-all'], 'http://www.findandconnect.gov.au', self.cache, "http://www.findandconnect.gov.au/cache", source, self.temp, 512),
        ]
        for case in cases:
            actions, base, cache, cache_url, source, output, expected_count = case
            try:
                crawler = Crawler.Crawler(actions, base, source, output, cache, cache_url)
                crawler.run()
            except:
                logging.error("Could not complete crawl job", exc_info=True)
                self.fail("Could not complete crawl job")
            # count the number of files in the output folder
            result_count = 0
            for filename in [f for f in os.listdir(output) if f.endswith(".htm") or f.endswith(".html")]:
                result_count += 1
            self.assertEqual(expected_count, result_count)
            # the file hash index should be present in the output folder
            path = output + os.sep + Cfg.HASH_INDEX_FILENAME
            self.assertEqual(True, os.path.exists(path))
            # the number of entries in the index should be the same as the file count
            hash_index = Utils.loadFileHashIndex(output)
            self.assertEqual(expected_count, len(hash_index))
            # the image cache folder should exist
            self.assertEqual(True, os.path.exists(self.cache))

    def test_crawl_html_all_with_update_on_first_run(self):
        """
        When the crawler is invoked to index a new site for the first time and
        it given the --update option, it should add all discovered content to the
        cache in the first pass.
        """
        actions = ['html-all']
        base = 'http://www.findandconnect.gov.au'
        cache = self.cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_original = self.source + os.sep + "update_original"
        expected_count = 4
        # crawl the source_original folder to establish the baseline
        crawler = Crawler.Crawler(actions, base, source_original, output, cache, cache_url, update=True)
        crawler.run()
        # the cache folder should have content in it now
        result_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".htm") or f.endswith(".html")]:
            result_count += 1
        self.assertEqual(expected_count, result_count)

    def test_crawl_with_exclude_directories(self):
        """
        It should crawl the input folder for HTML files and skip those
        directories identified in the exclude list.
        """
        source = self.module_path + os.sep + "crawl" + os.sep + "exclude"
        cases = [
            (['biogs'], ['html-all'], 'http://www.findandconnect.gov.au', self.cache, "http://www.findandconnect.gov.au/cache", source, self.temp, 0),
            (['eac','E000003b.htm'], ['html-all'], 'http://www.findandconnect.gov.au', self.cache, "http://www.findandconnect.gov.au/cache", source, self.temp, 2),
            (['E(.*)','b(.*)'], ['html-all'], 'http://www.findandconnect.gov.au', self.cache, "http://www.findandconnect.gov.au/cache", source, self.temp, 0),
            (['eac','E000001.xml','E000003.xml'], ['eaccpf'], 'http://www.findandconnect.gov.au', self.cache, "http://www.findandconnect.gov.au/cache", source, self.temp, 1),
            (['vic'], ['eaccpf'], 'http://www.findandconnect.gov.au', self.cache, "http://www.findandconnect.gov.au/cache", source, self.temp, 0),
        ]
        for case in cases:
            exclude, actions, base, cache, cache_url, source, output, expected_count = case
            try:
                crawler = Crawler.Crawler(actions, base, source, output, cache, cache_url, exclude=exclude)
                crawler.run()
            except:
                logging.error("Could not complete crawl job", exc_info=True)
                self.fail("Could not complete crawl job")
            # count the number of files in the output folder
            result_count = 0
            for filename in [f for f in os.listdir(output) if f != Cfg.HASH_INDEX_FILENAME]:
                result_count += 1
            self.assertEqual(expected_count, result_count)
            # the file hash index should be present in the output folder
            path = output + os.sep + Cfg.HASH_INDEX_FILENAME
            self.assertEqual(True, os.path.exists(path))
            # the number of entries in the index should be the same as the file count
            hash_index = Utils.loadFileHashIndex(output)
            self.assertEqual(expected_count, len(hash_index))

    def test_crawl_with_exclude_files(self):
        """
        It should crawl the input folder for HTML files and skip those
        identified in the exclude list.
        """
        source = self.module_path + os.sep + "crawl" + os.sep + "exclude"
        cases = [
            (['E000003b.htm'], ['html-all'], 'http://www.findandconnect.gov.au', self.cache, "http://www.findandconnect.gov.au/cache", source, self.temp, 2),
            (['E000001b.htm','E000003b.htm'], ['html-all'], 'http://www.findandconnect.gov.au', self.cache, "http://www.findandconnect.gov.au/cache", source, self.temp, 1),
            (['E(.*).htm'], ['html-all'], 'http://www.findandconnect.gov.au', self.cache, "http://www.findandconnect.gov.au/cache", source, self.temp, 0),
            (['E000003.xml'], ['eaccpf'], 'http://www.findandconnect.gov.au', self.cache, "http://www.findandconnect.gov.au/cache", source, self.temp, 2),
            (['E(.*).xml'], ['eaccpf'], 'http://www.findandconnect.gov.au', self.cache, "http://www.findandconnect.gov.au/cache", source, self.temp, 0),
            (['E000001.xml','E000003.xml'], ['eaccpf'], 'http://www.findandconnect.gov.au', self.cache, "http://www.findandconnect.gov.au/cache", source, self.temp, 1),
        ]
        for case in cases:
            exclude, actions, base, cache, cache_url, source, output, expected_count = case
            try:
                crawler = Crawler.Crawler(actions, base, source, output, cache, cache_url, exclude=exclude)
                crawler.run()
            except:
                logging.error("Could not complete crawl job", exc_info=True)
                self.fail("Could not complete crawl job")
            # count the number of files in the output folder
            result_count = 0
            for filename in [f for f in os.listdir(output) if f != Cfg.HASH_INDEX_FILENAME]:
                result_count += 1
            self.assertEqual(expected_count, result_count)
            # the file hash index should be present in the output folder
            path = output + os.sep + Cfg.HASH_INDEX_FILENAME
            self.assertEqual(True, os.path.exists(path))
            # the number of entries in the index should be the same as the file count
            hash_index = Utils.loadFileHashIndex(output)
            self.assertEqual(expected_count, len(hash_index))


if __name__ == '__main__':
    unittest.main()
