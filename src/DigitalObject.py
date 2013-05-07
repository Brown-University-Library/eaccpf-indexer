'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from HtmlPage import HtmlPage

import logging
import os
import urlparse
import yaml

class DigitalObject(object):
    '''
    An image or video file with associated metadata. The digital object is
    identified inside of an EAC-CPF document. That document provides metadata
    and a URL to a web page that presents the digital object. The web page
    must be parsed to extract a URL to the actual digital object file. Once
    the digital object is in hand, we create alternate thumbnail 
    representations of that file. The digital object metadata is recorded in
    a YAML file. Field names in the YAML record conform with the indexing 
    fields specified in the EAC-CPF Apache Solr schema.
    
    @see https://bitbucket.org/esrc/eaccpf-solr
    '''

    def __init__(self, Source, MetadataUrl, PresentationUrl, Title, Abstract, EntityType, LocalType, UnitDate):
        '''
        Source is a file system path or URL to the EAC-CPF document that 
        defines the digital object. MetadataUrl is a publc URL to the 
        EAC-CPF document that holds the primary digital object metadata. 
        PresentationUrl is a public URL to the HTML page the presents the 
        digital object.
        '''
        self.logger = logging.getLogger('DigitalObject')
        self.source = Source
        self.record = {}
        self.record['metadata_url'] = MetadataUrl
        self.record['presentation_url'] = PresentationUrl
        self.record['title'] = Title
        self.record['abstract'] = Abstract
        self.record['type'] = EntityType
        self.record['localtype'] = LocalType
        self.record['unitdate'] = UnitDate
        # parse the unit date into from and to dates
        fromDate, toDate = self._getDateRange(UnitDate)
        if fromDate:
            self.record['fromDate'] = fromDate
        if toDate:
            self.record['toDate'] = toDate
        # determine the source and public URL for the digital object
        if 'http://' in self.source or 'https://' in self.source:
            self.record['dobj_url'] = self._getObjectSourceUrl() 
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
            for a,b in zip(pth,url):
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
            # get the URL to the digital object file
            html = HtmlPage(html_path)
            self.record['dobj_url'] = html.getDigitalObjectUrl() 
            url = urlparse.urlparse(self.record['dobj_url'])
            # determine the path to the digital object file
            self.dobjpath = pth_base + url[2]
        # extract metadata from the HTML document
        self.record['dobj_type'] = self.getType()
        self.record['id'] = self.getRecordId()

    def _getDateRange(self, UnitDate):
        '''
        Parse unit date field to produce fromDate and toDate field values.
        @todo need to figure out what form these dates should be in!!!
        '''
        if UnitDate:
            return '0000-01-01T00:00:00Z', '0000-01-01T00:00:00Z'
        return None, None

    def _getObjectSourceUrl(self):
        '''
        Extract the digital object source file URL from its HTML record page.
        
        If the digital object was indexed from the file system, then we need
        to convert between 
        '''
        html = HtmlPage(self.record['presentation_url'])
        return html.getDigitalObjectUrl()

    def getFileName(self):
        '''
        Get the metadata file name.
        '''
        if "/" in self.record['metadata_url']:
            parts = self.record['metadata_url'].split("/")
            return parts[-1]
        return self.record['metadata_url']

    def getMetadataUrl(self):
        '''
        Get the public URL to the EAC-CPF metadata document that identifies
        this digital object.
        '''
        return self.record['metadata_url']

    def getPresentationUrl(self):
        '''
        Get the public URL to the HTML presentation.
        '''
        return self.record['presentation_url']

    def getRecord(self):
        '''
        Get the metadata record.
        '''
        return self.record

    def getRecordId(self):
        '''
        Get the record identifier.
        '''
        filename = self.getFileName()
        recordid, _ = os.path.splitext(filename)
        return recordid

    def getSourceUrl(self):
        '''
        Get the public URL for the digital object file.
        '''
        return self.record['dobj_url']

    def getType(self):
        '''
        Determine the type of data a URL represents.
        '''
        images = ['.gif','.jpg','.jpeg','.png']
        video = ['.avi','.mp4','.mpg','.mepg']
        _, ext = os.path.splitext(self.record['dobj_url'])
        if ext: 
            if ext.lower() in images:
                return 'image'
            elif ext.lower() in video:
                return 'video'
        return 'other'
    
    def write(self, Path, Id=None, CacheRecord=None):
        '''
        Write a YML representation of the digital object to the specified path.
        '''
        record = self.record
        if CacheRecord:
            for key in CacheRecord:
                record[key] = CacheRecord[key]
        if Id:
            filename = Id + '.yml'
            record['id'] = Id
        else:
            filename = self.getRecordId() + '.yml'
        data = yaml.dump(record, default_flow_style=False, indent=4)
        outfile = open(Path + os.sep + filename,'w')
        outfile.write(data)
        outfile.close()
        self.logger.info("Stored digital object YML " + filename)
