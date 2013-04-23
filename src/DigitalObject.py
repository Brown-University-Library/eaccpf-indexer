'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from HtmlPage import HtmlPage

import logging
import os
import yaml

class DigitalObject(object):
    '''
    An image or video file and associated metadata. Transforms the metadata 
    contained in the EAC-CPF record and HTML page to an intermediate YML 
    representation.
    
    <resourceRelation resourceRelationType="other" xlink:type="simple" xlink:href="http://www.findandconnect.gov.au/wa/objects/WD0000203.htm">
        <relationEntry localType="digitalObject">
            The 'Homes' Herald, 1978 [Methodist Homes for Children]
        </relationEntry>
        <objectXMLWrap>...</objectXMLWrap>
    </resourceRelation>
    '''

    def __init__(self, MetadataUrl, PresentationUrl, Title, Abstract, EntityType, LocalType, UnitDate):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('DigitalObject')
        self.record = {}
        self.record['metadata_url'] = MetadataUrl
        self.record['presentation_url'] = PresentationUrl
        self.record['title'] = Title
        self.record['abstract'] = Abstract
        self.record['type'] = EntityType
        self.record['localtype'] = LocalType
        self.record['unitdate'] = UnitDate
        self.record['dobj_url'] = self._getObjectSourceUrl()
        self.record['dobj_type'] = self.getType()
        self.record['id'] = self.getRecordId()
        # parse the unit date into from and to dates
        fromDate, toDate = self._getDateRange(UnitDate)
        if fromDate:
            self.record['fromDate'] = fromDate
        if toDate:
            self.record['toDate'] = toDate

    def _getDateRange(self, UnitDate):
        '''
        Parse unit date field to produce fromDate and toDate field values.
        @todo need to figure out what form these dates should be in!!!
        '''
        if UnitDate:
            return '0000-01-01T00:00:00Z', '0000-01-01T00:00:00Z'
        return None, None
    
    def _getFileName(self, Url):
        '''
        Get the file name from a URL.
        '''
        if "/" in Url:
            parts = Url.split("/")
            return parts[-1]
        return Url

    def _getObjectSourceUrl(self):
        '''
        Extract the digital object source file URL from its HTML record page.
        '''
        html = HtmlPage(self.record['presentation_url'])
        return html.getDigitalObjectUrl()

    def getFileName(self):
        '''
        Get the metadata file name.
        '''
        return self._getFileName(self.record['metadata_url'])

    def getRecord(self):
        '''
        Get the metadata record.
        '''
        return self.record

    def getRecordId(self):
        '''
        Get the record identifier.
        '''
        filename = self._getFileName(self.record['presentation_url'])
        recordid, _ = os.path.splitext(filename)
        return recordid

    def getSourceUrl(self):
        '''
        Get the URL for the digital object file.
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
