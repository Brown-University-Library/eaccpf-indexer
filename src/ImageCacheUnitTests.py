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
from ImageCache import ImageCache

class ImageCacheUnitTests(unittest.TestCase):
    '''
    Executes unit tests against the image cache module.
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
        It should create an object instance and a concomitant file system store
        for the image cache.
        '''
        # no path specified, no init
        self.assertRaises(Exception, ImageCache(self.path))
        # path specified, no init
        cache = ImageCache(self.path, False)
        self.assertNotEqual(cache,None)
        self.assertEquals(cache.path,self.path)
        self.assertEquals(os.path.exists(self.path),True)
        # path specified, init
        cache = ImageCache(self.path, True)
        self.assertNotEqual(cache,None)
        self.assertEquals(cache.path,self.path)
        self.assertEquals(os.path.exists(self.path),True)
    
    def test_getFileName(self):
        '''
        It should get the file name from a specified URL.
        '''
        cache = ImageCache(self.path)
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
        cache = ImageCache(self.path)
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
        cache = ImageCache(self.path)
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
        It should resize an image file to the specified dimensions.
        '''
        cache = ImageCache(self.path)
        images = [
                  "http://www.findandconnect.gov.au/site/images/aus-logo.png",
                  "http://www.findandconnect.gov.au/tas/site/images/logo-tasmania.png",
                  "http://www.findandconnect.gov.au/tas/objects/images/barrington_lodge_exterior.jpg",
                  "http://www.findandconnect.gov.au/vic/objects/thumbs/tn_TALLY%20HO%20VILLAGE%20-%20ADMINISTRATION%20BUILDING,%201980'S.png",
                  "http://www.findandconnect.gov.au/vic/objects/images/BM1-12A%20(355bl).jpg",
                  "http://www.findandconnect.gov.au/vic/objects/images/typing%20allambie.jpg",
                  ]
        for image in images:
            response = urllib2.urlopen(image)
            data = response.read()
            ext = cache._getFileNameExtension(image)
            temp = tempfile.mktemp(suffix="." + ext)
            # write downloaded file
            outfile = open(temp,'w')
            outfile.write(data)
            outfile.close()
            self.assertNotEqual(os.path.exists(temp),None)
            self.assertNotEqual(os.path.getsize(temp),0)
            # get the source image dimensions
            img = Image.open(temp)
            source_width, source_height = img.size
            del(img)
            # resize the image
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
    
    def test_store_and_retrieve(self):
        '''
        It should store the data object and return a key. It should return the 
        source data when queried with the item key.
        '''
        images = [
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_All%20on%20Together%20Govt%20Rec%20Home%20photoarticle59448843-3-001.png",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_Allandale%20Boys%20Cottage.png",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_aust_inland_mission.png",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_Kalumburu.png",
                  "http://www.findandconnect.gov.au/wa/objects/thumbs/tn_Kartanup.png",
                  ]
        keys = {}
        cache = ImageCache(self.path)
        # download the source images to a temporary directory
        for image in images:
            response = urllib2.urlopen(image)
            data = response.read()
            filename = cache._getFileName(image)
            # write downloaded file
            outfile = open(self.temp + os.sep + filename,'w')
            outfile.write(data)
            outfile.close()
        # put images into the cache, save the item key
        for filename in os.listdir(self.temp):
            path = self.temp + os.sep + filename
            key, objpath = cache.store(path)
            self.assertNotEqual(key,None)
            keys[key]= objpath
        # fetch images from the cache using the key
        copydir = tempfile.mkdtemp()
        for key in keys:
            source, filename, data = cache.retrieve(key)
            self.assertNotEqual(source,None)
            self.assertNotEqual(filename,None)
            self.assertNotEqual(data,None)
            path = copydir + os.sep + filename
            outfile = open(path,'w')
            outfile.write(data)
            outfile.close()
        # delete temporary files
        self._rmdir(copydir)
        self.assertEqual(os.path.exists(copydir), False)
        
if __name__ == "__main__":
    unittest.main()
