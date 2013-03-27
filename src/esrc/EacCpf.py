'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from lxml import etree
import logging
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
    
    def getDigitalObjects(self):
        '''
        Get the list of digital objects referenced in the document.
        '''
        return []
