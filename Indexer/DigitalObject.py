"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

import HtmlPage
import Utils
import logging
import os
import yaml


IMAGE_FILE_EXT = ['.gif','.jpg','.jpeg','.png']
VIDEO_FILE_EXT = ['.avi','.mp4','.mpg','.mpeg']


def load_metadata_on_demand(func):
    """
    If the digital object metadata has not been loaded from the HTML
    presentation page, then load it and store it in the object.
    """
    def wrapper(self, *args, **kwargs):
        # if the local file system digital object source path has not been
        # determined yet
        if not hasattr(self, 'dobj_source'):
            # The documents are being indexed through the file system. We know
            # the local path for the source EAC-CPF document where the digital
            # object is declared. We also know the public URL to the same
            # EAC-CPF document and the URL to the HTML page where the digital
            # object is presented. We need to determine the local file system
            # path to that HTML document. Once we have that, we can determine
            # local file system path to the source digital object file.
            ### Step 1: find the local path to the HTML file
            pth = self.source.split('/')
            url = self.metadata_url.replace('http://','').replace('https://','').split('/')
            pth.reverse()
            url.reverse()
            for a,b in zip(pth, url):
                if a == b:
                    pth.remove(a)
                    url.remove(b)
            pth.reverse()
            url.reverse()
            # the web site and file system roots
            url_base = 'http://' + '/'.join(url)
            pth_base = '/'.join(pth)
            # the file system path to the HTML document
            html_path = os.path.abspath(pth_base + self.presentation_url.replace(url_base,''))
            # Step 2: load the HTML page then get the URL to the source
            # digital object file
            html = HtmlPage.HtmlPage(html_path)
            dobj_url = html.getDigitalObjectUrl()
            # Step 3: set properties
            self.dobj_source = pth_base + dobj_url.replace(url_base, '')
            _, ext = os.path.splitext(self.dobj_source)
            if ext and ext.lower() in IMAGE_FILE_EXT:
                self.dobj_type = 'image'
            elif ext and ext.lower() in VIDEO_FILE_EXT:
                self.dobj_type = 'video'
            else:
                self.dobj_type = 'other'
            # object id
            filename = Utils.getFileName(self.presentation_url)
            self.dobj_id, _ = os.path.splitext(filename)
        # execute the function that was called
        return func(self, *args, **kwargs)
    return wrapper


class DigitalObject(object):
    """
    An image or video file and associated metadata. Digital objects are
    declared in the resourceRelations section of an EAC-CPF document. That
    document provides metadata and a URL to a web page that in turn presents
    the digital object. The web page must be parsed to extract a URL to the
    actual digital object file.

    Parsing of the HTML document does not occur when the Digital Object is
    created. Instead, the function decorator @load_metadata_on_demand loads
    the HTML content when one of the decorated instance functions is called.
    Metadata is cached in the object at that point.

    Metadata can be written out to a YAML file. Field names in the YAML record
    conform with those specified in the EAC-CPF Apache Solr schema.

    @see https://bitbucket.org/esrc/eaccpf-solr
    """

    def __init__(self, Source, MetadataUrl, PresentationUrl, Title, Abstract,
                 LocalType, FromDate=None, ToDate=None, UnitDate=None,
                 AlternateTitle=None):
        """
        Source is a file system path or URL to the EAC-CPF document that 
        defines the digital object. MetadataUrl is a public URL to the
        EAC-CPF document that holds the primary digital object metadata. 
        PresentationUrl is a public URL to the HTML page the presents the 
        digital object.
        """
        self.abstract = Abstract
        self.local_type = LocalType
        self.logger = logging.getLogger()
        self.metadata_url = MetadataUrl
        self.presentation_url = PresentationUrl
        self.record = None
        self.source = Source
        self.title = Title
        self.type = 'Digital Object' # ISSUE #23
        if AlternateTitle:
            self.alternate_title = AlternateTitle
        if FromDate:
            self.fromDate = FromDate
        if ToDate:
            self.toDate = ToDate
        if UnitDate:
            self.unit_date = UnitDate
            self.fromDate, self.toDate = Utils.parseUnitDate(UnitDate)

    def getAbstract(self):
        """
        Get the digital object abstract.
        """
        return self.abstract

    def getFileName(self):
        """
        Get the metadata file name.
        """
        return Utils.getFileName(self.metadata_url)

    def getLocalType(self):
        """
        Get the localtype.
        """
        return self.local_type

    def getMetadataUrl(self):
        """
        Get the public URL to the EAC-CPF metadata document that identifies
        this digital object.
        """
        return self.metadata_url

    @load_metadata_on_demand
    def getObjectId(self):
        """
        Get the digital object identifier.
        """
        return self.dobj_id

    def getPresentationUrl(self):
        """
        Get the public URL to the HTML presentation.
        """
        return self.presentation_url

    @load_metadata_on_demand
    def getRecord(self):
        """
        Get the metadata record.
        """
        record = {}
        record['id'] = self.getRecordId()
        record['source'] = self.source
        record['metadata_url'] = self.metadata_url
        record['presentation_url'] = self.presentation_url
        record['title'] = self.title
        record['abstract'] = self.abstract
        record['type'] = self.type
        record['localtype'] = self.local_type
        if hasattr(self, 'unitdate'):
            record['unitdate'] = self.unit_date
        if hasattr(self, 'fromDate'):
            record['fromDate'] = self.fromDate
        if hasattr(self, 'toDate'):
            record['toDate'] = self.toDate
        if hasattr(self, 'alternate_title'):
            record['alternate_title'] = self.alternate_title
        record['dobj_id'] = self.getObjectId()
        record['dobj_source'] = self.getSourceUrl()
        record['dobj_type'] = self.getType()
        return record

    def getRecordId(self):
        """
        Get the record identifier.
        """
        filename = Utils.getFileName(self.metadata_url)
        recordid, _ = os.path.splitext(filename)
        return recordid

    @load_metadata_on_demand
    def getSourceUrl(self):
        """
        Get the public URL for the digital object file.
        """
        return self.dobj_source

    def getTitle(self):
        """
        Get the title.
        """
        return self.title

    @load_metadata_on_demand
    def getType(self):
        """
        Determine the type of data a URL represents.
        """
        return self.dobj_type

    @load_metadata_on_demand
    def write(self, Path, Id=None, CacheRecord=None):
        """
        Write a YML representation of the digital object to the specified path.
        """
        filename = "{0}.yml".format(self.getObjectId())
        record = self.getRecord()
        if Id:
            record['id'] = Id
            filename = "{0}.yml".format(record['id'])
        if CacheRecord:
            for key in CacheRecord:
                record[key] = CacheRecord[key]
        # write the file
        data = yaml.dump(record, default_flow_style=False, indent=4)
        with open(Path + os.sep + filename, 'w') as outfile:
            outfile.write(data)
        self.logger.info("Stored digital object {0}".format(filename))
