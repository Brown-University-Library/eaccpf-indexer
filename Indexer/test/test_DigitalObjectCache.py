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

import logging
import os
import random
import string
import tempfile
import unittest
import urllib2


class TestDigitalObjectCache(unittest.TestCase):
    """
    Executes unit tests against the digital object cache module.
    """
    
    def _generate(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def _rmdir(self,d):
        """
        Recursively delete a directory.
        @author ActiveState
        @see http://code.activestate.com/recipes/552732-remove-directories-recursively/
        """
        for path in (os.path.join(d,f) for f in os.listdir(d)):
            if os.path.isdir(path):
                self._rmdir(path)
            else:
                os.unlink(path)
        os.rmdir(d)

    def setUp(self):
        """
        Create a path for the temporary cache.
        """
        self.path = "/tmp/cache"
        self.temp = tempfile.mkdtemp()
        self.url_root = "http://test.com/"

    def tearDown(self):
        """
        Clean up temporary directories.
        """
        if (os.path.exists(self.path)):
            self._rmdir(self.path)
        if (os.path.exists(self.temp)):
            self._rmdir(self.temp)
        self.assertNotEqual(os.path.exists(self.path),True)
        self.assertNotEqual(os.path.exists(self.temp),True)

    def test_init(self):
        """
        It should create an object instance and a concomitant file system for
        the image cache.
        """
        # no path/urlroot specified, no init
        self.assertRaises(Exception, DigitalObjectCache.DigitalObjectCache(self.path))
        # path specified, no url_root or init
        cache = DigitalObjectCache.DigitalObjectCache(self.path)
        self.assertNotEqual(cache, None)
        self.assertEquals(cache.path, self.path)
        self.assertEquals(cache.url_root, '/')
        self.assertEquals(os.path.exists(self.path), True)
        # path, url_root, init specified
        cache = DigitalObjectCache.DigitalObjectCache(self.path, UrlRoot=self.url_root, Init=True)
        self.assertNotEqual(cache, None)
        self.assertEquals(cache.path, self.path)
        self.assertEquals(cache.url_root, self.url_root)
        self.assertEquals(os.path.exists(self.path),True)

    def test_getHash(self):
        """
        It should return the same hash for the file each time it is run.
        """
        # cache = DigitalObjectCache(self.path)
        # urls = [
        #          "http://www.findandconnect.gov.au/site/images/aus-logo.png",
        #          "http://www.findandconnect.gov.au/tas/site/images/logo-tasmania.png",
        #          "http://www.findandconnect.gov.au/tas/objects/images/barrington_lodge_exterior.jpg",
        #          "http://www.findandconnect.gov.au/vic/objects/thumbs/tn_TALLY%20HO%20VILLAGE%20-%20ADMINISTRATION%20BUILDING,%201980'S.png",
        #          "http://www.findandconnect.gov.au/vic/objects/images/BM1-12A%20(355bl).jpg",
        #          "http://www.findandconnect.gov.au/vic/objects/images/typing%20allambie.jpg",
        # ]
        # for url in urls:
        #     # download the test file
        #     response = urllib2.urlopen(url)
        #     data = response.read()
        #     ext = cache._getFileNameExtension(url)
        #     temp = tempfile.mktemp(suffix="." + ext)
        #     outfile = open(temp,'w')
        #     outfile.write(data)
        #     outfile.close()
        #     # run multiple passes on the file and compare results
        #     firsthash = cache._getHash(temp)
        #     for _ in range(10):
        #         newhash = cache._getHash(temp)
        #         self.assertEqual(firsthash, newhash)
        #     # delete the test file
        #     os.remove(temp)
        #     self.assertEqual(os.path.exists(temp),False)

    def test_resizeImage(self):
        """
        It should resize the image to the specified dimensions.
        @todo move test assets into the local testing folder
        """
        cache = DigitalObjectCache.DigitalObjectCache(self.path)
        cases = [
                  "http://www.findandconnect.gov.au/assets/img/social-twitter.png",
                  "http://www.findandconnect.gov.au/assets/img/header-logo-narrow.png",
                  "http://www.findandconnect.gov.au/assets/img/footer-logo.png"
        ]
        for case in cases:
            try:
                response = urllib2.urlopen(case)
                data = response.read()
            except:
                self.fail("Could not load resource {0}".format(case))
            ext = Utils.getFileNameExtension(case)
            temp = tempfile.mktemp(suffix="." + ext)
            # write downloaded file
            with open(temp,'w') as f:
                f.write(data)
            self.assertNotEqual(os.path.exists(temp),None)
            self.assertNotEqual(os.path.getsize(temp),0)
            # get the source case dimensions
            img = Image.open(temp)
            source_width, source_height = img.size
            del(img)
            # resize the case
            resized = cache._resizeImageAndSaveToNewFile(temp, 260, 180)
            img = Image.open(resized)
            resized_width, resized_height = img.size
            self.assertGreaterEqual(source_width, resized_width)
            self.assertGreaterEqual(source_height, resized_height)
            # delete the temp file
            os.remove(temp)
            os.remove(resized)
            self.assertEqual(os.path.exists(temp),False)
            self.assertEqual(os.path.exists(resized),False)
    
    def test_put_and_get(self):
        """
        It should put the data obj and return an identifier. It should 
        return the source data when queried with the item key.
        @todo move test assets into the local testing folder
        """
        cases = [
                  "http://www.findandconnect.gov.au/cache/fcwa/8d/9b/d9/b6/de/b3/5f/17/ca/32/f7/7c/ba/86/4d/e0/11/c3/94/ff/obj/medium.png",
                  "http://www.findandconnect.gov.au/cache/fcwa/41/32/f6/96/2c/09/f2/dd/74/23/8a/e9/71/b9/e4/c2/7b/65/63/11/obj/medium.png",
                  "http://www.findandconnect.gov.au/cache/fcwa/02/8a/26/f7/6f/22/f7/a3/05/b9/e6/40/2e/13/41/c4/41/b4/8a/5b/obj/medium.png",
        ]
        baseurl = "http://www.findandconnect.gov.au/cache"
        records = {}
        cache = DigitalObjectCache.DigitalObjectCache(self.path,baseurl)
        # add files to cache
        for case in cases:
            # #26 Image files must be accessible on the local disk before they
            # can be processed
            temp = Utils.getTemporaryFileFromResource(case)
            record = cache.put(temp)
            self.assertNotEqual(record, None)
            self.assertNotEqual(record['cache_id'], None)
            cacheid = record['cache_id']
            records[cacheid]= record
        # fetch cases from the cache using the key
        tmpdir = tempfile.mkdtemp()
        for key in records.keys():
            obj = cache.get(key)
            self.assertNotEqual(obj['dobj_source'], None)
            self.assertNotEqual(obj['dobj_file_name'], None)
            self.assertNotEqual(obj['dobj_file_extension'], None)
            self.assertNotEqual(obj['dobj_proxy_large'], None)
            self.assertNotEqual(obj['dobj_proxy_medium'], None)
            self.assertNotEqual(obj['dobj_proxy_small'], None)
        # delete temporary files
        self._rmdir(tmpdir)
        self.assertEqual(os.path.exists(tmpdir), False)
        
if __name__ == "__main__":
    unittest.main()
