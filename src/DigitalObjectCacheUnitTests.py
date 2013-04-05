'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

import Image
import os
import random
import string
import unittest
import urllib2
import tempfile
from DigitalObjectCache import DigitalObjectCache

class DigitalObjectCacheUnitTests(unittest.TestCase):
    '''
    Executes unit tests against the digital object cache module.
    '''
    
    def _generate(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def _rmdir(self,d):
        '''
        Recursively delete a directory.
        @author ActiveState
        @see http://code.activestate.com/recipes/552732-remove-directories-recursively/
        '''
        for path in (os.path.join(d,f) for f in os.listdir(d)):
            if os.path.isdir(path):
                self._rmdir(path)
            else:
                os.unlink(path)
        os.rmdir(d)

    def setUp(self):
        '''
        Create a path for the temporary cache.
        '''
        self.path = "/tmp/cache"
        self.temp = tempfile.mkdtemp()

    def tearDown(self):
        '''
        Clean up temporary directories.
        '''
        if (os.path.exists(self.path)):
            self._rmdir(self.path)
        if (os.path.exists(self.temp)):
            self._rmdir(self.temp)
        self.assertNotEqual(os.path.exists(self.path),True)
        self.assertNotEqual(os.path.exists(self.temp),True)

    def test_init(self):
        '''
        It should create an object instance and a concomitant file system put
        for the image cache.
        '''
        # no path specified, no init
        self.assertRaises(Exception, DigitalObjectCache(self.path))
        # path specified, no init
        cache = DigitalObjectCache(self.path, init=False)
        self.assertNotEqual(cache,None)
        self.assertEquals(cache.path,self.path)
        self.assertEquals(os.path.exists(self.path),True)
        # path specified, init
        cache = DigitalObjectCache(self.path, init=True)
        self.assertNotEqual(cache,None)
        self.assertEquals(cache.path,self.path)
        self.assertEquals(os.path.exists(self.path),True)
        # base url specified
        cache = DigitalObjectCache(self.path, 'http://www.example.com/')
        self.assertNotEqual(cache,None)
        self.assertEquals(cache.path,self.path)
        self.assertEquals('http://www.example.com/',cache.base)
    
    def test_getFileName(self):
        '''
        It should get the file name from a specified URL.
        '''
        cache = DigitalObjectCache(self.path)
        paths = {
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_All%20on%20Together%20Govt%20Rec%20Home%20photoarticle59448843-3-001.png" : "tn_All%20on%20Together%20Govt%20Rec%20Home%20photoarticle59448843-3-001.png",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_Allandale%20Boys%20Cottage.png" : "tn_Allandale%20Boys%20Cottage.png",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_aust_inland_mission.png" : "tn_aust_inland_mission.png",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_Kalumburu.png" : "tn_Kalumburu.png",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_Kartanup.png" : "tn_Kartanup.png",
                 }
        for path in paths:
            filename = cache._getFileName(path)
            self.assertNotEqual(filename, None)
            self.assertEquals(filename, paths[path])
    
    def test_getFileNameExtension(self):
        '''
        It should get the file name extension from a specified URL.
        '''
        cache = DigitalObjectCache(self.path)
        paths = {
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_Allandale%20Boys%20Cottage.htm" : "htm",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_aust_inland_mission.jpg" : "jpg",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_Kalumburu.png" : "png",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_Kartanup.pdf" : "pdf",
                 }
        for path in paths:
            extension = cache._getFileNameExtension(path)
            self.assertNotEqual(extension, None)
            self.assertEquals(extension, paths[path])
            
    def test_getHash(self):
        '''
        It should return the same hash for the file each time it is run.
        '''
        cache = DigitalObjectCache(self.path)
        urls = [
                 "http://www.findandconnect.gov.au/site/images/aus-logo.png",
                 "http://www.findandconnect.gov.au/tas/site/images/logo-tasmania.png",
                 "http://www.findandconnect.gov.au/tas/objects/images/barrington_lodge_exterior.jpg",
                  "http://www.findandconnect.gov.au/vic/objects/thumbs/tn_TALLY%20HO%20VILLAGE%20-%20ADMINISTRATION%20BUILDING,%201980'S.png",
                  "http://www.findandconnect.gov.au/vic/objects/images/BM1-12A%20(355bl).jpg",
                  "http://www.findandconnect.gov.au/vic/objects/images/typing%20allambie.jpg",
                ]
        for url in urls:
            # download the test file
            response = urllib2.urlopen(url)
            data = response.read()
            ext = cache._getFileNameExtension(url)
            temp = tempfile.mktemp(suffix="." + ext)
            outfile = open(temp,'w')
            outfile.write(data)
            outfile.close()
            # run multiple passes on the file and compare results
            firsthash = cache._getHash(temp)
            for _ in range(10):
                newhash = cache._getHash(temp)
                self.assertEqual(firsthash, newhash)
            # delete the test file
            os.remove(temp)
            self.assertEqual(os.path.exists(temp),False)

    def test_resizeImage(self):
        '''
        It should resize an case file to the specified dimensions.
        '''
        cache = DigitalObjectCache(self.path)
        cases = [
                  "http://www.findandconnect.gov.au/site/images/aus-logo.png",
                  "http://www.findandconnect.gov.au/tas/site/images/logo-tasmania.png",
                  "http://www.findandconnect.gov.au/tas/objects/images/barrington_lodge_exterior.jpg",
                  "http://www.findandconnect.gov.au/vic/objects/thumbs/tn_TALLY%20HO%20VILLAGE%20-%20ADMINISTRATION%20BUILDING,%201980'S.png",
                  "http://www.findandconnect.gov.au/vic/objects/images/BM1-12A%20(355bl).jpg",
                  "http://www.findandconnect.gov.au/vic/objects/images/typing%20allambie.jpg",
                  ]
        for case in cases:
            response = urllib2.urlopen(case)
            data = response.read()
            ext = cache._getFileNameExtension(case)
            temp = tempfile.mktemp(suffix="." + ext)
            # write downloaded file
            outfile = open(temp,'w')
            outfile.write(data)
            outfile.close()
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
        '''
        It should put the data obj and return an identifier. It should 
        return the source data when queried with the item key.
        '''
        cases = [
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_All%20on%20Together%20Govt%20Rec%20Home%20photoarticle59448843-3-001.png",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_Allandale%20Boys%20Cottage.png",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_aust_inland_mission.png",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_Kalumburu.png",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_Kartanup.png",
                  ]
        baseurl = "http://www.findandconnect.gov.au/cache"
        records = {}
        cache = DigitalObjectCache(self.path,baseurl)
        # add files to cache
        for case in cases:
            record = cache.put(case)
            self.assertNotEqual(record,None)
            self.assertNotEqual(record['id'],None)
            cacheid = record['id']
            records[cacheid]= record
        # fetch cases from the cache using the key
        tmpdir = tempfile.mkdtemp()
        for key in records.keys():
            obj = cache.get(key)
            self.assertNotEqual(obj['source'],None)
            self.assertNotEqual(obj['file-name'],None)
            self.assertNotEqual(obj['file-extension'],None)
            self.assertNotEqual(obj['large-url'],None)
            self.assertNotEqual(obj['medium-url'],None)
            self.assertNotEqual(obj['small-url'],None)
        # delete temporary files
        self._rmdir(tmpdir)
        self.assertEqual(os.path.exists(tmpdir), False)
        
if __name__ == "__main__":
    unittest.main()
