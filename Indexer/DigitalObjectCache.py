"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from PIL import Image

from . import Utils
import hashlib
import logging
import os
import shutil
import yaml

METADATA_FILENAME = "object.yml"


class DigitalObjectCache(object):
    """
    Storage for source and alternate sized representations of a digital
    object. The cache is implemented as a simple file system store. The
    cache folder contains one subdirectory for each stored object. The
    object/subdirectory name is the SHA1 hash for the object metadata
    record. Inside the subdirectory, a YAML file named object.yml is
    stored with the object metadata, along with small, medium and large
    cached image files.
    """

    def __init__(self, Path, BaseURL):
        self.logger = logging.getLogger()
        self.path = Path
        self.url_root = BaseURL if BaseURL.endswith('/') else BaseURL + '/'
        # create the cache folder if it doesn't already exist
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def _resizeImageAndSaveToNewFile(self, Source, Destination, Width, Height):
        """
        Resize the image to the specified height and width and save the updated
        image to a new file. If the image's existing height and width are less 
        than those specified, then the original dimensions are maintained. 
        Return the new file path.
        """
        ext = Utils.getFileNameExtension(Source)
        # load the image
        img = Image.open(Source)
        # convert color mode
        if img.mode != "RGB":
            img = img.convert("RGB")
        # resize the image if required
        existwidth, existheight = img.size
        if (Width < existwidth or Height < existheight):
            size = Width, Height
            img.thumbnail(size, Image.ANTIALIAS)
        # save the image to the a file
        fmt = ext.upper()
        fmt = 'JPEG' if fmt == 'JPG' else fmt
        img.save(Destination, fmt)

    def delete(self, filename):
        """
        Delete the digital object matching the specified Id.
        """
        path = self.path + os.sep + filename
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        else:
            os.remove(path)

    def get(self, Id):
        """
        Get the digital object record corresponding with the specified ID. If
        no object is found, return None.
        """
        with open(self.path + os.sep + Id + os.sep + METADATA_FILENAME) as f:
            data = f.read()
            return yaml.load(data)

    def get_all(self):
        """
        Get a list of all digital objects.
        """
        return [d for d in os.listdir(self.path) if os.path.isdir(self.path + os.sep + d)]

    def get_cache_identifier(self, filename):
        """
        Get the cache identifier for the corresponding record ID.
        """
        # return hashlib.sha1(filename).hexdigest()
        return Utils.getRecordIdFromFilename(filename)

    def purge(self, keep_files=None):
        """
        Purge the cache of any digital object not present in the filename list.
        """
        if keep_files:
            # transform the filenames into cache identifiers
            keep_ids = []
            for filename in keep_files:
                keep_ids.append(self.get_cache_identifier(filename))
            # remove all cache objects not represented in the keep_ids list
            cache_objects = os.listdir(self.path)
            for cache_id in [o for o in cache_objects if not o in keep_ids]:
                self.delete(cache_id)
        else:
            for cache_id in os.listdir(self.path):
                self.delete(cache_id)

    def put(self, record_id, source):
        """
        Store the digital object source file, located at the specified file
        system path, in the cache. Generate alternate image representations
        of the digital object. Return the digital object record.

        Cached data is stored in a subfolder of the cache directory. The
        folder name is a SHA1 hash of the record ID.
        """
        cache_id = self.get_cache_identifier(record_id)
        source_hash = Utils.getFileHash(source)
        source_filename = Utils.getFileName(source)
        source_extension = Utils.getFileNameExtension(source_filename)
        # determine the URL for the object cache folder
        url = self.url_root + cache_id
        # create the digital object folder
        obj_cache_path = self.path + os.sep + cache_id
        if not os.path.exists(obj_cache_path):
            os.mkdir(obj_cache_path)
        # create alternately sized image representations and write them into
        # the object folder
        large_filename = "large." + source_extension
        medium_filename = "medium." + source_extension
        small_filename = "small." + source_extension
        large_url = url + "/" + large_filename
        medium_url = url + "/" +  medium_filename
        small_url = url + "/" + small_filename
        self._resizeImageAndSaveToNewFile(source, obj_cache_path + os.sep + large_filename, 320, 320)
        self._resizeImageAndSaveToNewFile(source, obj_cache_path + os.sep + medium_filename, 260, 180)
        self._resizeImageAndSaveToNewFile(source, obj_cache_path + os.sep + small_filename, 130, 90)
        # create a record for the digital object that will be stored in the
        # cache folder and returned to the caller
        record = {}
        record['cache_id'] = cache_id
        record['dobj_metadata_id'] = Utils.getRecordIdFromFilename(record_id)
        record['dobj_metadata_filename'] = record_id
        record['dobj_source'] = source
        record['dobj_hash'] = source_hash
        record['dobj_file_name'] = source_filename
        record['dobj_file_extension'] = source_extension
        record['dobj_proxy_large'] = large_url
        record['dobj_proxy_medium'] = medium_url
        record['dobj_proxy_small'] = small_url
        record['dobj_proxy_source'] = small_url
        # write the digital object record into the folder
        with open(obj_cache_path + os.sep + METADATA_FILENAME, 'w') as f:
            data = yaml.dump(record, default_flow_style=False, indent=4)
            f.write(data)
        # return the digital object record
        return record
