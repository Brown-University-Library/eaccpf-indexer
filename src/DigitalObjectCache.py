'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

import Image
import hashlib
import logging
import os
import shutil
import tempfile
import urllib
import urllib2
from pairtree import PairtreeStorageFactory

class DigitalObjectCache(object):
    '''
    Storage for source and alternate sized representations of a digital 
    object.
    '''

    def __init__(self, Path, BaseUrl='', init=False):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('DigitalObjectCache')
        self.path = Path
        if BaseUrl.endswith('/'):
            self.base = BaseUrl
        else:
            self.base = BaseUrl + '/'
        # Create the parent directories for the storage path if they don't 
        # exist. If you create the pairtree folder itself, it requires the 
        # pairtree metadata files in it before getting the put. Otherwise, it 
        # will throw a pairtree.storage_exceptions.NotAPairtreeStoreException
        parent = os.path.dirname(self.path)
        if not os.path.exists(parent):
            os.makedirs(parent)
        # create the pairtree storage
        factory = PairtreeStorageFactory()
        try:
            self.storage = factory.get_store(store_dir=self.path, uri_base="http://")
        except:
            self.logger.critical("Could not initialize the image cache")
            raise

    def _clearFiles(self, path):
        '''
        Delete all files within the specified path.
        '''
        files = os.listdir(path)
        for filename in files:
            os.remove(path + os.sep + filename)

    def _getFileName(self, Filename):
        '''
        Get the filename from the specified URI or path.
        '''
        if "/" in Filename:
            parts = Filename.split("/")
            return parts[-1]
        return Filename

    def _getFileNameExtension(self, Filename):
        '''
        Get the filename extension. If an extension is not found, return None.
        '''
        if "." in Filename:
            parts = Filename.split(".")
            return parts[-1]
        return None
    
    def _getHash(self, Path):
        '''
        Get a hash of the specified file.
        '''
        hasher = hashlib.md5()
        infile = open(Path,'r')
        hasher.update(infile.read())
        infile.close()
        return hasher.hexdigest()
    
    def _getPathRelativeToCacheRoot(self, Path):
        '''
        Get the path relative to the cache root.
        '''
        Path = Path.replace(self.path,'')
        return Path.replace('/pairtree_root/','')
    
    def _isUrl(self, Path):
        '''
        Determine if the source is a URL or a file system path.
        '''
        if Path != None and ("http:" in Path or "https:" in Path):
            return True
        return False

    def _makeCache(self, Path, init=False):
        '''
        Create a cache folder at the specified Path if none exists. If the Path 
        already exists, delete all files.
        '''
        if not os.path.exists(Path):
            os.makedirs(Path)
            self.logger.info("Created cache folder at " + Path)
        else:
            if (init):
                self._rmdir(Path)
                os.makedirs(Path)
                self.logger.info("Cleared cache folder at " + Path)

    def _resizeImageAndSaveToNewFile(self, Source, Width, Height):
        '''
        Resize the image to the specified height and width and save the updated
        image to a new file. If the image's existing height and width are less 
        than those specified, then the original dimensions are maintained. 
        Return the new file path.
        '''
        # set output file
        ext = self._getFileNameExtension(Source)
        filepath = tempfile.mktemp(suffix="." + ext)
        # load the image
        im = Image.open(Source)
        # convert color mode
        if im.mode != "RGB":
            im = im.convert("RGB")
        # resize the image if required
        existwidth, existheight = im.size
        if (Width < existwidth or Height < existheight):
            size = Width, Height
            im.thumbnail(size, Image.ANTIALIAS)
        # save the image to the new file
        fmt = ext.upper()
        if fmt == 'JPG':
            fmt = "JPEG"
        im.save(filepath, fmt)
        # return new image path
        return filepath

    def _rmdir(self,d):
        '''
        Recursively delete a directory.
        @author ActiveState
        @see http://code.activestate.com/recipes/552732-remove-directories-recursively/
        '''
        if (os.path.exists(d)):
            for path in (os.path.join(d,f) for f in os.listdir(d)):
                if os.path.isdir(path): 
                    self._rmdir(path)
                else:
                    os.unlink(path)
            os.rmdir(d)

    def get(self, Id):
        '''url
        Get the source URI, source filename and file data as identified by
        the specified key. If no object is found, return None.
        '''
        try:
            obj = self.storage.get_object(Id)
            if obj:
                record = {}
                record['cache_id'] = Id
                record['dobj_url'] = obj.get_bytestream("dobj_url")
                record['dobj_file_name'] = obj.get_bytestream("dobj_file_name")
                record['dobj_file_extension'] = obj.get_bytestream("dobj_file_extension")
                record['dobj_proxy_large'] = obj.get_bytestream("dobj_proxy_large")
                record['dobj_proxy_medium'] = obj.get_bytestream("dobj_proxy_medium")
                record['dobj_proxy_small'] = obj.get_bytestream("dobj_proxy_small")
                return record
        except:
            return None

    def put(self, Source):
        '''
        Store the digital object located at the specified Source location in 
        the file storage. Generate alternate image representations of the 
        digital object. Return a record with the cache identifier, object 
        source URL, and URLs to the cached alternate representations.
        '''
        # source file name
        filename = self._getFileName(Source)
        ext = self._getFileNameExtension(filename)
        # write source object to temporary file
        digitalObject = tempfile.mktemp(suffix="." + ext)
        if (self._isUrl(Source)):
            # replace spaces in URL before downloading
            url = Source.replace(' ','%20')
            # download file
            response = urllib2.urlopen(url)
            data = response.read()
            outfile = open(digitalObject,'w')
            outfile.write(data)
            outfile.close()
        else:
            shutil.copyfile(Source, digitalObject)
        # generate an id for the object
        cacheid = self._getHash(digitalObject)
        # determine the URL for the cache root
        path = self.storage._id_to_dirpath(cacheid) + os.sep
        path = self._getPathRelativeToCacheRoot(path)
        if self.base:
            url = self.base + path
        else:
            url = path
        try:
            # create a new cache object
            obj = self.storage.get_object(cacheid, create_if_doesnt_exist=True)
            # set object source location, file name and extension 
            obj.add_bytestream("dobj_url",Source)
            obj.add_bytestream("dobj_file_name",filename)
            obj.add_bytestream("dobj_file_extension",ext)
            # create alternate representations
            large = digitalObject # no change
            medium = self._resizeImageAndSaveToNewFile(digitalObject, 260, 180)
            small = self._resizeImageAndSaveToNewFile(digitalObject, 130, 90)
            # create alternate representations for the object
            large_filename = "large." + ext
            medium_filename = "medium." + ext
            small_filename = "small." + ext
            with open(large,'rb') as stream:
                obj.add_bytestream(large_filename,stream)
            with open(medium,'rb') as stream:
                obj.add_bytestream(medium_filename,stream)
            with open(small,'rb') as stream:
                obj.add_bytestream(small_filename,stream)
            # store URLs to alternates
            large_url = url + large_filename
            medium_url = url + medium_filename
            small_url = url + small_filename
            obj.add_bytestream("dobj_proxy_large",large_url)
            obj.add_bytestream("dobj_proxy_medium",medium_url)
            obj.add_bytestream("dobj_proxy_small",small_url)
            # delete the temporary files
            os.remove(large)
            os.remove(medium)
            os.remove(small)
            # return the object record
            record = {}
            record['cache_id'] = cacheid
            record['dobj_url'] = Source
            record['dobj_file_name'] = filename
            record['dobj_file_extension'] = ext
            record['dobj_proxy_large'] = large_url
            record['dobj_proxy_medium'] = medium_url
            record['dobj_proxy_small'] = small_url
            return record
        except:
            self.logger.warning("Could not write %s to the cache" % Source)
