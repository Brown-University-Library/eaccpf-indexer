"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from PIL import Image

import Utils
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

    def delete(self, Id):
        """
        Delete the digital object matching the specified Id.
        """
        shutil.rmtree(self.path + os.sep + Id, ignore_errors=True)

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

    def purge(self, DoNotPurge=None):
        """
        Purge the cache of any digital object not present in the do not purge
        list.
        """
        if DoNotPurge:
            for cache_id in [o for o in os.listdir(self.path) if not o in DoNotPurge]:
                self.delete(cache_id)
        else:
            for cache_id in os.listdir(self.path):
                self.delete(cache_id)

    def put(self, Id, Source):
        """
        Store the digital object source file, located at the specified file
        system path, in the cache. Generate alternate image representations
        of the digital object. Return the digital object record.
        """
        source_hash = Utils.getFileHash(Source)
        source_filename = Utils.getFileName(Source)
        source_extension = Utils.getFileNameExtension(source_filename)
        # determine the URL for the object cache folder
        url = self.url_root + Id
        # create the digital object folder
        obj_cache_path = self.path + os.sep + Id
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
        self._resizeImageAndSaveToNewFile(Source, obj_cache_path + os.sep + large_filename, 320, 320)
        self._resizeImageAndSaveToNewFile(Source, obj_cache_path + os.sep + medium_filename, 260, 180)
        self._resizeImageAndSaveToNewFile(Source, obj_cache_path + os.sep + small_filename, 130, 90)
        # create a record for the digital object that will be stored in the
        # cache folder and returned to the caller
        record = {}
        record['cache_id'] = Id
        record['dobj_source'] = Source
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
