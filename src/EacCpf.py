'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from BeautifulSoup import BeautifulSoup
from DigitalObject import DigitalObject
import logging
import os
import urllib2

class EacCpf(object):
    '''
    An EAC-CPF document.
    '''

    def __init__(self, Source, Presentation):
        '''
        Constructor
        '''
        # logger
        self.logger = logging.getLogger('EacCpf')
        self.source = Source
        self.presentation = Presentation
        # load the document content
        self._load()
    
    def _getFileName(self, Url):
        '''
        Get the file name from a URL.
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
    
    def _getLocation(self):
        '''
        '''
        pass
    
    def _getTagString(self,Tag):
        '''
        '''
        if Tag and Tag.string:
            return str(Tag.string)
        return None
        
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
            metadata = str(self.source)
            presentation = Record['xlink:href'].encode("utf-8")
            title = str(entry.string)
            abstract = self._getTagString(Record.find('abstract'))
            entitytype = self.getEntityType()
            localtype = self.getLocalType()
            # location
            unitdate = self._getTagString(Record.find('unitdate'))
            dobj = DigitalObject(metadata,presentation,title,abstract,entitytype,localtype,unitdate)
            return dobj
        # no digital object found
        return None

    def getDigitalObjects(self):
        '''
        Get the list of digital objects referenced in the document.
        '''
        dobjects = []
        soup = BeautifulSoup(self.data)
        resources = soup.findAll('resourcerelation')
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
    
    def getFileName(self):
        '''
        Get document file name.
        '''
        return self._getFileName(self.source)
    
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
    
    def getRecordId(self):
        '''
        Get the record identifier.
        @todo the identifier should come from the data rather than the file name
        '''
        return self._getId(self.source)
    
    def hasDigitalObjects(self):
        '''
        Determine if the EAC-CPF record has digital object references.
        '''
        objects = self.getDigitalObjects()
        if objects and len(objects) > 0:
            return True
        return False
    
    def write(self, Path):
        '''
        Write the EAC-CPF data to the specified path.
        '''
        outfile = (Path + os.sep + self.getFileName(),'w')
        outfile.write(self.data)
        outfile.write('\n<!-- @Source=%(Source)s @referrer=%(referrer)s -->' % {"Source":self.source, "referrer":self.presentation})
        outfile.close()
