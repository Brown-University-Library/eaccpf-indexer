"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from HtmlPage import HtmlPage

import Utils
import logging
import os
import urlparse
import yaml


class DigitalObject(object):
    """
    An image or video file with associated metadata. The digital object is
    identified inside of an EAC-CPF document. That document provides metadata
    and a URL to a web page that presents the digital object. The web page
    must be parsed to extract a URL to the actual digital object file. Once
    the digital object is in hand, we create alternate thumbnail 
    representations of that file. The digital object metadata is recorded in
    a YAML file. Field names in the YAML record conform with the indexing 
    fields specified in the EAC-CPF Apache Solr schema.
    
    @see https://bitbucket.org/esrc/eaccpf-solr
    """

    def __init__(self, Source, MetadataUrl, PresentationUrl, Title, Abstract, LocalType, FromDate=None, ToDate=None, UnitDate=None, AlternateTitle=None):
        """
        Source is a file system path or URL to the EAC-CPF document that 
        defines the digital object. MetadataUrl is a publc URL to the 
        EAC-CPF document that holds the primary digital object metadata. 
        PresentationUrl is a public URL to the HTML page the presents the 
        digital object.
        """
        self.logger = logging.getLogger()
        self.source = Source
        self.metadata_url = MetadataUrl
        self.presentation_url = PresentationUrl
        self.title = Title
        self.abstract = Abstract
        self.type = 'Digital Object' # ISSUE #23
        self.localtype = LocalType
        if UnitDate:
            self.unitdate = UnitDate
            self.fromDate, self.toDate= Utils.parseUnitDate(UnitDate)
        if FromDate:
            self.fromDate = FromDate
        if ToDate:
            self.toDate = ToDate
        if AlternateTitle:
            self.alternate_title = AlternateTitle
        # determine the source and public URL for the digital object
        if 'http://' in self.source or 'https://' in self.source:
            html = HtmlPage(self.presentation_url)
            self.dobj_source = html.getDigitalObjectUrl()
        else:
            # The documents are being indexed through the file system. 
            # Consequently, we need to determine what the file system paths are 
            # to the HTML and digital object files. We currently know the 
            # EAC-CPF file path and URL, and the HTML document URL. Here we 
            # determine the file system path to the HTML document from that.
            pth = Source.split('/')
            url = MetadataUrl.replace('http://','').replace('https://','').split('/')
            pth.reverse()
            url.reverse()
            for a,b in zip(pth, url):
                if a == b:
                    pth.remove(a) 
                    url.remove(b)
            pth.reverse()
            url.reverse()
            # the web site and file system roots
            pth_base = '/'.join(pth)
            url_base = 'http://' + '/'.join(url)
            # the file system path to the HTML document
            html_path = pth_base + PresentationUrl.replace(url_base,'')
            # the next step is to determine the file system path to the digital
            # object file with the information we have on hand
            html = HtmlPage(html_path)
            dobj_url = html.getDigitalObjectUrl()
            dobj_path = pth_base + dobj_url.replace(url_base, '')
            self.dobj_source = dobj_path
        # extract metadata from the HTML document
        self.dobj_type = self.getType()
        self.id = self.getObjectId()

    def getFileName(self):
        """
        Get the metadata file name.
        """
        return Utils.getFileName(self.metadata_url)

    def getMetadataUrl(self):
        """
        Get the public URL to the EAC-CPF metadata document that identifies
        this digital object.
        """
        return self.metadata_url

    def getObjectId(self):
        """
        Get the digital object identifier.
        """
        name = Utils.getFileName(self.presentation_url)
        return Utils.getRecordIdFromFilename(name)

    def getPresentationUrl(self):
        """
        Get the public URL to the HTML presentation.
        """
        return self.presentation_url

    def getRecord(self):
        """
        Get the metadata record.
        """
        record = {}
        record['id'] = self.id
        record['source'] = self.source
        record['metadata_url'] = self.metadata_url
        record['presentation_url'] = self.presentation_url
        record['title'] = self.title
        record['abstract'] = self.abstract
        record['type'] = self.type
        record['localtype'] = self.localtype
        if hasattr(self, 'unitdate'):
            record['unitdate'] = self.unitdate
        if hasattr(self, 'fromDate'):
            record['fromDate'] = self.fromDate
        if hasattr(self, 'toDate'):
            record['toDate'] = self.toDate
        if hasattr(self, 'alternate_title'):
            record['alternate_title'] = self.alternate_title
        record['dobj_source'] = self.dobj_source
        record['dobj_type'] = self.dobj_type
        return record

    def getRecordId(self):
        """
        Get the record identifier.
        """
        filename = self.getFileName()
        recordid, _ = os.path.splitext(filename)
        return recordid

    def getSourceUrl(self):
        """
        Get the public URL for the digital object file.
        """
        return self.dobj_source

    def getType(self):
        """
        Determine the type of data a URL represents.
        """
        images = ['.gif','.jpg','.jpeg','.png']
        video = ['.avi','.mp4','.mpg','.mepg']
        _, ext = os.path.splitext(self.dobj_source)
        if ext: 
            if ext.lower() in images:
                return 'image'
            elif ext.lower() in video:
                return 'video'
        return 'other'
    
    def write(self, Path, Id=None, CacheRecord=None):
        """
        Write a YML representation of the digital object to the specified path.
        """
        filename = self.getObjectId() + ".yml"
        record = self.getRecord()
        if Id:
            record['id'] = Id
            filename = record['id'] + ".yml"
        if CacheRecord:
            for key in CacheRecord:
                record[key] = CacheRecord[key]
        # write the file
        data = yaml.dump(record, default_flow_style=False, indent=4)
        outfile = open(Path + os.sep + filename, 'w')
        outfile.write(data)
        outfile.close()
        self.logger.info("Stored digital object {0}".format(filename))
