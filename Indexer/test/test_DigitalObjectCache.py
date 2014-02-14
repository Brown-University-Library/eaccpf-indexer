"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from Indexer import DigitalObjectCache
from Indexer import Utils

try:
    from PIL import Image
except:
    import Image

import inspect
import os
import random
import shutil
import tempfile
import unittest


class TestDigitalObjectCache(unittest.TestCase):
    """
    Executes unit tests against the digital object cache module.
    """
    
    def setUp(self):
        """
        Create a path for the temporary cache.
        """
        self.cache = tempfile.mkdtemp()
        self.cache_url = '/'
        self.module = os.path.abspath(inspect.getfile(self.__class__))
        self.module_path = os.path.dirname(self.module)
        self.temp = tempfile.mkdtemp()
        self.url_root = "http://test.com/"

    def tearDown(self):
        """
        Clean up temporary directories.
        """
        shutil.rmtree(self.cache, ignore_errors=True)
        shutil.rmtree(self.temp, ignore_errors=True)

    def test_init(self):
        """
        It should create a digital object cache instance and file storage.
        """
        cache = DigitalObjectCache.DigitalObjectCache(self.cache, self.cache_url)
        self.assertNotEqual(cache, None)
        self.assertEquals(cache.path, self.cache)
        self.assertEquals(cache.url_root, '/')
        self.assertEquals(os.path.exists(self.cache), True)

    def test_init_with_root_and_init_option(self):
        """
        It should create a digital object cache instance and file storage.
        """
        cache = DigitalObjectCache.DigitalObjectCache(self.cache, self.url_root)
        self.assertNotEqual(cache, None)
        self.assertEquals(cache.path, self.cache)
        self.assertEquals(cache.url_root, self.url_root)
        self.assertEquals(os.path.exists(self.cache),True)

    def test_resizeImage(self):
        """
        It should resize the image to the specified dimensions.
        """
        cache = DigitalObjectCache.DigitalObjectCache(self.cache, self.cache_url)
        test_files_path = self.module_path + os.sep + "digitalobjectcache" + os.sep + "resize_image" + os.sep
        cases = ["1.jpg","2.jpg","3.jpg"]
        for filename in cases:
            # copy the test file to the temp folder
            source_file = test_files_path + os.sep + filename
            source_file_extension = Utils.getFileNameExtension(filename)
            test_file = tempfile.mktemp(suffix="." + source_file_extension)
            # get the source case dimensions
            img = Image.open(source_file)
            source_width, source_height = img.size
            # resize the image
            cache._resizeImageAndSaveToNewFile(source_file, test_file, 260, 180)
            img = Image.open(test_file)
            resized_width, resized_height = img.size
            self.assertGreaterEqual(source_width, resized_width)
            self.assertGreaterEqual(source_height, resized_height)
            # clean up
            os.remove(test_file)

    def test_purge(self):
        """
        It should purge the cache of all files.
        """
        cache = DigitalObjectCache.DigitalObjectCache(self.cache, self.cache_url)
        test_files_path = self.module_path + os.sep + "digitalobjectcache" + os.sep + "resize_image" + os.sep
        cases = [
            "social-twitter.png",
            "header-logo-narrow.png",
            "footer-logo.png"
        ]
        # add all test files to the cache
        for filename in cases:
            path = test_files_path + filename
            cache.put(filename, path)
        # purge the cache
        cache.purge()
        # get the cached file count
        actual_count = len(os.listdir(cache.path))
        self.assertEqual(0, actual_count)

    def test_purge_by_index(self):
        """
        It should purge the cache of any file not represented in the index.
        """
        cache = DigitalObjectCache.DigitalObjectCache(self.cache, self.cache_url)
        test_files_path = self.module_path + os.sep + "digitalobjectcache" + os.sep + "resize_image" + os.sep
        cases = [
            "social-twitter.png",
            "header-logo-narrow.png",
            "footer-logo.png"
        ]
        # create a filename to hash map of the test files
        fn_hash_map = {}
        for filename in cases:
            fn_hash_map[filename] = Utils.getFileHash(test_files_path, filename)
        # add all the test files to the cache
        for filename in cases:
            path = test_files_path + filename
            cache.put(fn_hash_map[filename], path)
        # remove a random file from the filename to hash map
        keys = fn_hash_map.keys()
        rand = random.Random()
        i = rand.randrange(0,len(keys)-1)
        fn_hash_map.pop(keys[i])
        # purge the index
        cache.purge(fn_hash_map.values())
        # count the number of files in the cache
        actual_count = len(os.listdir(cache.path))
        expected_count = len(cases) - 1
        self.assertEqual(expected_count, actual_count)

    def test_put_and_get(self):
        """
        It should put the data obj and return an identifier. It should 
        return the source data when queried with the item key.
        """
        cache = DigitalObjectCache.DigitalObjectCache(self.cache, self.cache_url)
        test_files_path = self.module_path + os.sep + "digitalobjectcache" + os.sep + "resize_image" + os.sep
        cases = [
            "social-twitter.png",
            "header-logo-narrow.png",
            "footer-logo.png"
        ]
        records = {}
        for filename in os.listdir(test_files_path):
            record = cache.put(filename, test_files_path + filename)
            self.assertNotEqual(record, None)
            self.assertNotEqual(record['cache_id'], None)
            cacheid = record['cache_id']
            records[cacheid]= record
        # fetch cases from the cache using the key
        for key in records.keys():
            obj = cache.get(key)
            self.assertEqual(key, obj['cache_id'])
            self.assertNotEqual(obj['dobj_source'], None)
            self.assertNotEqual(obj['dobj_file_name'], None)
            self.assertNotEqual(obj['dobj_file_extension'], None)
            self.assertNotEqual(obj['dobj_proxy_large'], None)
            self.assertNotEqual(obj['dobj_proxy_medium'], None)
            self.assertNotEqual(obj['dobj_proxy_small'], None)

if __name__ == "__main__":
    unittest.main()
