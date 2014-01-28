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
        self.module = os.path.abspath(inspect.getfile(self.__class__))
        self.module_path = os.path.dirname(self.module)
        self.source = self.module_path + os.sep + "crawl"
        self.temp = tempfile.mkdtemp()
        self.temp_cache_parent = tempfile.mkdtemp()
        self.temp_cache = self.temp_cache_parent + os.sep + "image_cache"

    def tearDown(self):
        """
        Tear down the test environment.
        """
        if os.path.exists(self.temp):
            shutil.rmtree(self.temp, ignore_errors=True)
        if os.path.exists(self.temp_cache_parent):
            shutil.rmtree(self.temp_cache_parent, ignore_errors=True)

    def test__init__(self):
        """
        It should create a crawler instance.
        """
        source = self.source + os.sep + "update_original"
        cases = [
            (['eaccpf'], 'http://www.example.com', self.temp_cache, "http://www.example.com/cache", source, self.temp),
            ([], 'http://www.example.com', self.temp_cache, "http://www.example.com/cache", source, self.temp),
        ]
        for case in cases:
            actions, base, cache, cache_url, source, output = case
            try:
                crawler = Crawler.Crawler(actions, base, cache, cache_url, source, output)
            except:
                logging.error("Could not create Crawler instance", exc_info=True)
                self.fail("Could not create Crawler instance")

    def test_crawl(self):
        """
        It should retrieve files that exist. For each EAC-CPF file, it should
        add the metadata and presentation URLs as attributes to the eac-cpf
        node.
        """
        source = self.source + os.sep + "update_original"
        cases = [
            (['eaccpf'], 'http://www.findandconnect.gov.au', self.temp_cache, "http://www.findandconnect.gov.au/cache", source, self.temp, 3),
        ]
        for case in cases:
            actions, base, cache, cache_url, source, output, expected_count = case
            try:
                crawler = Crawler.Crawler(actions, base, cache, cache_url, source, output)
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
            self.assertEqual(True, os.path.exists(self.temp_cache))

    def test_crawl_eaccpf_update_add(self):
        """
        It should index a source folder and create an index of the stored
        files. When a subsequent index is executed, it should add any new
        files into the output folder and update the file index.
        """
        actions = ['eaccpf']
        base = 'http://www.findandconnect.gov.au'
        cache = self.temp_cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_add = self.source + os.sep + "update_add"
        source_original = self.source + os.sep + "update_original"
        expected_count = 4
        # crawl the source_original folder to establish the baseline
        crawler = Crawler.Crawler(actions, base, cache, cache_url, source_original, output)
        crawler.run()
        # crawl the source_add folder to process the changes
        crawler = Crawler.Crawler(actions, base, cache, cache_url, source_add, output, update=True)
        crawler.run()
        # the output folder should now contain four eac-cpf documents
        result_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".xml")]:
            result_count += 1
        self.assertEqual(expected_count, result_count)
        # the hash index should now contain four records
        hash_index = Utils.loadFileHashIndex(output)
        self.assertEqual(expected_count, len(hash_index))

    def test_crawl_eaccpf_update_change(self):
        """
        It should index a source
        """
        actions = ['eaccpf']
        base = 'http://www.findandconnect.gov.au'
        cache = self.temp_cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_add = self.source + os.sep + "update_delete"
        source_original = self.source + os.sep + "update_original"
        # crawl the source_original folder to establish the baseline
        crawler = Crawler.Crawler(actions, base, cache, cache_url, source_original, output)
        crawler.run()
        # record the output file count and index file hash
        original_file_count = len(os.listdir(output))
        original_index_hash = Utils.getFileHash(output + os.sep + Cfg.HASH_INDEX_FILENAME)
        # crawl the source_add folder to process the changes
        crawler = Crawler.Crawler(actions, base, cache, cache_url, source_add, output, update=True)
        crawler.run()
        # the output file count should be equal to the new output file count
        updated_file_count = len(os.listdir(output))
        # the updated index file hash should be different from the original
        # output file index
        updated_index_hash = Utils.getFileHash(output + os.sep + Cfg.HASH_INDEX_FILENAME)
        self.assertNotEqual(updated_index_hash, original_index_hash)

    def test_crawl_eaccpf_update_delete(self):
        """
        It should index a source folder and create an index of the stored
        files. When a subsequent index is executed, it should delete any
        files that have been removed from the source, update the output
        folder and file index.
        """
        actions = ['eaccpf']
        base = 'http://www.findandconnect.gov.au'
        cache = self.temp_cache
        cache_url = "http://www.findandconnect.gov.au/cache"
        output = self.temp
        source_add = self.source + os.sep + "update_delete"
        source_original = self.source + os.sep + "update_original"
        expected_count = 2
        # crawl the source_original folder to establish the baseline
        crawler = Crawler.Crawler(actions, base, cache, cache_url, source_original, output)
        crawler.run()
        # crawl the source_add folder to process the changes
        crawler = Crawler.Crawler(actions, base, cache, cache_url, source_add, output, update=True)
        crawler.run()
        # the output folder should now contain four eac-cpf documents
        result_count = 0
        for filename in [f for f in os.listdir(output) if f.endswith(".xml")]:
            result_count += 1
        self.assertEqual(expected_count, result_count)
        # the hash index should now contain four records
        hash_index = Utils.loadFileHashIndex(output)
        self.assertEqual(expected_count, len(hash_index))


if __name__ == '__main__':
    unittest.main()
