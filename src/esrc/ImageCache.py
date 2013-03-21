'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

import Image
import hashlib
import logging
import os
import tempfile
import urllib2
from pairtree import PairtreeStorageFactory

class ImageCache(object):
    '''
    Storage for thumbnails and alternate sized representations of an image.
    '''

    def __init__(self, Path, BaseUrl=None, init=False):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('feeder')
        self.path = Path
        self.base = BaseUrl
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

    def retrieve(self, Key):
        '''
        Retrieve the source URI, source filename and file data as identified by
        the specified key. If no object is found, return None.
        '''
        try:
            obj = self.storage.get_object(Key)
            source = obj.get_bytestream("source")
            filename = obj.get_bytestream("filename")
            data = obj.get_bytestream(filename)
            return source, filename, data
        except:
            return None

    def store(self, Source):
        '''
        Store image and metadata in the file store. Generate thumbnail image
        representation. Return the id of the stored image thumbnail.
        '''
        # generate file names
        source_filename = self._getFileName(Source)
        source_extension = self._getFileNameExtension(source_filename)
        tempfile_path = tempfile.mktemp(suffix="." + source_extension)
        # retrieve the source data and write it to a temporary file
        if (self._isUrl(Source)):
            response = urllib2.urlopen(Source)
            data = response.read()
            # write downloaded file
            outfile = open(tempfile_path,'w')
            outfile.write(data)
            outfile.close()
        else:
            tempfile_path = Source
        # generate an id for the file
        key = self._getHash(tempfile_path)
        try:
            # create thumbnail image
            thumbnail_path = self._resizeImageAndSaveToNewFile(tempfile_path, 260, 180)
            thumbnail_filename = self._getFileName(thumbnail_path)
            # put the thumbnail, source location, original filename into the storage
            # obj = self.storage.create_object(key)
            obj = self.storage.get_object(key, create_if_doesnt_exist=True)
            obj.add_bytestream("source",Source)
            obj.add_bytestream("filename",thumbnail_filename)
            with open(tempfile_path,'rb') as stream:
                obj.add_bytestream(thumbnail_filename,stream)
            # delete the temporary files
            os.remove(tempfile_path)
            os.remove(thumbnail_path)
            # log results
            path = self.storage._id_to_dirpath(key) + os.sep + thumbnail_filename
            path = self._getPathRelativeToCacheRoot(path)
            if self.base:
                uri = self.base + path
            else:
                uri = path
            # return the object id
            return key, uri
        except:
            self.logger.warning("Could not store %s" % Source)
