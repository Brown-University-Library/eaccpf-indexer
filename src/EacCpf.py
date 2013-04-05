'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from BeautifulSoup import BeautifulSoup
from HtmlPage import HtmlPage
import logging
import os
import urllib2

class EacCpf(object):
    '''
    An EAC-CPF document.
    '''

    def __init__(self, Source):
        '''
        Constructor
        '''
        # logger
        self.logger = logging.getLogger('EacCpf')
        self.source = Source
        # load the document content
        self._load()
    
    def _getDigitalObjectType(self, Url):
        '''
        Determine the type of data a URL represents.
        '''
        images = ['.gif','.jpg','.jpeg','.png']
        video = ['.avi','.mp4','.mpg','.mepg']
        _, ext = os.path.splitext(Url)
        if ext: 
            if ext.lower() in images:
                return 'image'
            elif ext.lower() in video:
                return 'video'
        return 'other'

    def _getDigitalObjectUrl(self, Source):
        '''
        Extract the digital object source file URL from its HTML record page.
        '''
        html = HtmlPage(Source)
        return html.getDigitalObjectUrl()
    
    def _getDateRange(self, UnitDate):
        '''
        Parse unit date field to produce fromDate and toDate field values.
        @todo need to figure out what form these dates should be in!!!
        '''
        return '2000-01-01', '2001-01-01'
    
    def _getFileName(self, Url):
        '''
        Get file name from URL.
        '''
        if "/" in Url:
            parts = Url.split("/")
            return parts[-1]
        return Url
        
    def _getId(self, Url):
        '''
        Get digital object identifier from the object URL.
        '''
        filename = self._getFileName(Url)
        recordid, _ = os.path.splitext(filename)
        return recordid
        
    def _isEACCPF(self, Path):
        '''
        Determines if the file at the specified path is EAC-CPF. 
        '''
        if Path.endswith("xml"):
            infile = open(Path,'r')
            data = infile.read()
            infile.close()
            if "<eac-cpf" in data and "</eac-cpf>" in data:
                return True
        return False

    def _isUrl(self, Source):
        '''
        Determine if the source reference is a URL.
        '''
        if Source != None and ("http:" in Source or "https:" in Source):
            return True
        return False

    def _load(self):
        '''
        Load the document content.
        '''
        if self._isUrl(self.source):
            response = urllib2.urlopen(self.source)
            self.data = response.read()
        else:
            infile = open(self.source)
            self.data = infile.read()
            infile.close()
        self.logger.debug("Loaded content for " + self.source)
        
    def getDigitalObject(self, Record):
        '''
        Transform the metadata contained in the HTML page to an intermediate 
        YML digital object representation.
        @see http://www.findandconnect.gov.au/wa/biogs/WE00006b.htm
        @see http://www.findandconnect.gov.au/wa/eac/WE00006.xml
        
        <resourceRelation resourceRelationType="other" xlink:type="simple" xlink:href="http://www.findandconnect.gov.au/wa/objects/WD0000203.htm">
            <relationEntry localType="digitalObject">
                The 'Homes' Herald, 1978 [Methodist Homes for Children]
            </relationEntry>
            <objectXMLWrap>...</objectXMLWrap>
        </resourceRelation>
        
        - it should return the image metadata (web page URL, image URL, image 
          title, image description, image location), in addition to the URL to 
          the image to be cached
        '''
        # if the resource contains a relationEntry with localType attribute = 'digitalObject'
        entry = Record.find('relationentry',{'localtype':'digitalObject'})
        if entry:
            # digital object record
            url = Record['xlink:href'].encode("utf-8")
            dobject = {}
            dobject['id'] = self._getId(url)
            dobject['metadata_url'] = self.source.encode("utf-8")
            dobject['presentation_url'] = url
            dobject['type'] = self.getEntityType()
            dobject['localtype'] = self.getLocalType()
            dobject['dobj_url'] = self._getDigitalObjectUrl(url)
            dobject['dobj_type'] = self._getDigitalObjectType(url)
            dobject['title'] = str(entry.string)
            # functions
            # date
            unitdate = Record.find('unitdate')
            if unitdate and unitdate.string:
                udate = unitdate.string.encode("utf-8")
                fromdate, todate = self._getDateRange(udate)
                if fromdate:
                    dobject['fromDate'] = fromdate
                if todate:
                    dobject['toDate'] = todate
            # abstract
            abstract = Record.find('abstract')
            if abstract and abstract.string:
                dobject['abstract'] = abstract.string.encode("utf-8")
            # @todo location
            return dobject
        # no digital object found
        return None

    def getDigitalObjects(self):
        '''
        Get the list of digital objects referenced in the document.
        '''
        soup = BeautifulSoup(self.data)
        resources = soup.findAll('resourcerelation')
        dobjects = []
        for resource in resources:
            dobject = self.getDigitalObject(resource)
            if dobject:
                dobjects.append(dobject)
        return dobjects
    
    def getEntityType(self):
        '''
        Get the entity type.
        '''
        soup = BeautifulSoup(self.data)
        try:
            etype = soup.find('entitytype')
            return etype.string.encode("utf-8")
        except:
            return None
    
    def getFunctions(self):
        '''
        Get the functions.
        '''
        soup = BeautifulSoup(self.data)
        functions = soup.findAll('function')
        result = []
        for function in functions:
            try:
                term = function.find("term")
                result.append(str(term.string))
            except:
                pass
        return result
    
    def getLocalType(self):
        '''
        Get the local type.
        '''
        soup = BeautifulSoup(self.data)
        try:
            ltype = soup.find('localcontrol').find('term')
            return ltype.string.encode("utf-8")
        except:
            return None
    
    def hasDigitalObjects(self):
        '''
        Determine if the EAC-CPF record has digital object references.
        '''
        objects = self.getDigitalObjects()
        if objects and len(objects) > 0:
            return True
        return False
