"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from pairtree import PairtreeStorageFactory
from PIL import Image
import Utils
import logging
import os
import shutil
import tempfile
import urllib2


class DigitalObjectCache(object):
    """
    Storage for source and alternate sized representations of a digital 
    object. The storage folder must either not exist when first creating
    the cache, or it must already be initialized as a Pairtree storage
    folder. If the folder exists and is not initialized, then it will
    throw a pairtree.storage_exceptions.NotAPairtreeStoreException
    """

    def __init__(self, Path, UrlRoot='', Init=False):
        """
        Constructor
        """
        self.logger = logging.getLogger()
        self.path = Path
        if UrlRoot.endswith('/'):
            self.url_root = UrlRoot
        else:
            self.url_root = UrlRoot + '/'
        if Init and os.path.exists(self.path):
            shutil.rmtree(self.path)
        # create the pairtree storage instance
        factory = PairtreeStorageFactory()
        try:
            self.storage = factory.get_store(store_dir=self.path, uri_base="http://")
        except:
            self.logger.critical("Could not initialize the image cache " + self.path)
            raise

    def _getPathRelativeToCacheRoot(self, Path):
        """
        Get the path relative to the cache root.
        """
        Path = Path.replace(self.path, '')
        return Path.replace('/pairtree_root/', '')
    
    def _resizeImageAndSaveToNewFile(self, Source, Width, Height):
        """
        Resize the image to the specified height and width and save the updated
        image to a new file. If the image's existing height and width are less 
        than those specified, then the original dimensions are maintained. 
        Return the new file path.
        @todo check image format type
        """
        # set output file
        ext = Utils.getFileNameExtension(Source)
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

    def get(self, Id):
        """
        Get the source URI, source filename and file data as identified by
        the specified key. If no object is found, return None.
        """
        try:
            obj = self.storage.get_object(Id)
            if obj:
                record = {}
                record['cache_id'] = Id
                record['dobj_source'] = obj.get_bytestream("dobj_source")
                record['dobj_file_name'] = obj.get_bytestream("dobj_file_name")
                record['dobj_file_extension'] = obj.get_bytestream("dobj_file_extension")
                record['dobj_proxy_large'] = obj.get_bytestream("dobj_proxy_large")
                record['dobj_proxy_medium'] = obj.get_bytestream("dobj_proxy_medium")
                record['dobj_proxy_small'] = obj.get_bytestream("dobj_proxy_small")
                return record
        except:
            return None

    def put(self, Source):
        """
        Store the digital object located at the specified file system source
        location in the file storage. Generate alternate image representations
        of the digital object. Return a record with the cache identifier,
        object source URL, and URLs to the cached alternate representations.
        """
        # generate an id for the object
        cache_id = Utils.getFileHash(Source)
        # determine the URL for the cache root
        path = self.storage._id_to_dirpath(cache_id) + os.sep
        path = self._getPathRelativeToCacheRoot(path)
        if self.url_root:
            url = self.url_root + path
        else:
            url = path
        # create a new cache object
        obj = self.storage.get_object(cache_id, create_if_doesnt_exist=True)
        # set object source location, file name and extension
        filename = Utils.getFileName(Source)
        ext = Utils.getFileNameExtension(filename)
        obj.add_bytestream("dobj_source", Source)
        obj.add_bytestream("dobj_file_name", filename)
        obj.add_bytestream("dobj_file_extension", ext)
        # create alternate representations
        large = Source # no change
        medium = self._resizeImageAndSaveToNewFile(Source, 260, 180)
        small = self._resizeImageAndSaveToNewFile(Source, 130, 90)
        # create alternate representations for the object
        large_filename = "large." + ext
        medium_filename = "medium." + ext
        small_filename = "small." + ext
        with open(large,'rb') as stream:
            obj.add_bytestream(large_filename, stream)
        with open(medium,'rb') as stream:
            obj.add_bytestream(medium_filename, stream)
        with open(small,'rb') as stream:
            obj.add_bytestream(small_filename, stream)
        # store URLs to alternates
        large_url = url + large_filename
        medium_url = url + medium_filename
        small_url = url + small_filename
        obj.add_bytestream("dobj_proxy_large", large_url)
        obj.add_bytestream("dobj_proxy_medium", medium_url)
        obj.add_bytestream("dobj_proxy_small", small_url)
        # delete the temporary files
        # os.remove(large)
        os.remove(medium)
        os.remove(small)
        # return the object record
        record = {}
        record['cache_id'] = cache_id
        record['dobj_source'] = Source
        record['dobj_file_name'] = filename
        record['dobj_file_extension'] = ext
        record['dobj_proxy_large'] = large_url
        record['dobj_proxy_medium'] = medium_url
        record['dobj_proxy_small'] = small_url
        return record
