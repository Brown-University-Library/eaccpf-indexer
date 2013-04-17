'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from BeautifulSoup import BeautifulSoup

import logging
import os
import re
import urllib2
import urlparse

class HtmlPage(object):
    '''
    HTML document pages contain metadata and references to external entities
    that are the subject of indexing. This class wraps the HTML document and
    provides convenience methods for extracting required metadata.
    '''

    def __init__(self, Source, BaseUrl=None):
        '''
        Source is a file system path or URL to the document. URL is an 
        optional argument specified when the document is being indexed from a 
        file system and the document contains relative URLs. If the document
        contains absolute URLs, then the URL parameter is ignored.
        '''
        self.logger = logging.getLogger('HtmlPage')
        self.source = Source
        self._load()
        if BaseUrl:
            if not BaseUrl.endswith('/'):
                BaseUrl = BaseUrl + '/'
            filename = self._getFileName(Source)        
            self.url = BaseUrl + filename

    def _getAbsoluteUrl(self,Base,Path):
        '''
        Get the absolute URL for a path.
        '''
        url = urlparse.urljoin(Base,Path)
        return url.replace(' ','%20')
        
    def _getDocumentParentPath(self, Path):
        '''
        Get the path to the parent of the specified directory.
        '''
        i = Path.rfind('/')
        return Path[:i+1]

    def _getDocumentParentUri(self, Uri):
        '''
        Get the parent directory of the file in the specified URL.  Non / 
        terminated URLs are treated as representing files.
        '''
        uri = self.getUrl()
        i = uri.rfind('/')
        url = uri[:i+1]
        return url.replace(' ','%20').encode("utf-8")

    def _getFileName(self, Url):
        '''
        Get the filename from the specified URI or path.
        '''
        if "/" in Url:
            parts = Url.split("/")
            return parts[-1]
        return Url

    def _getTagAttributeValueByName(self, Tags, Type, Attribute):
        '''l
        Get the value of the specified digital object field name from a list of
        tags. Return None if the field name can not be found.
        '''
        for tag in Tags:
            field = tag.find(Type)
            if field:
                val = field[Attribute]
                return val.encode("utf8")
        return None

    def _getTagContentByClass(self, Tags, Type, FieldName, Field='class'):
        '''
        Get the value of the specified digital object field name from a list of
        tags. Return None if the field name can not be found.
        '''
        for tag in Tags:
            field = tag.find(Type,{Field:FieldName})
            if field:
                return field.text.encode("utf8")
        return None
    
    def _getVisibleText(self, element):
        '''
        '''
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return ''
        result = re.sub('<!--.*-->|\r|\n', '', str(element), flags=re.DOTALL)
        result = re.sub('\s{2,}|&nbsp;', ' ', result)
        return result

    def _isUrl(self, Source):
        '''
        Determine if the source is a URL or a file system path.
        '''
        if Source != None and ("http://" in Source or "https://" in Source):
            return True
        return False
    
    def _load(self):
        '''
        Load the document content.
        '''
        if (self._isUrl(self.source)):
            response = urllib2.urlopen(self.source)
            self.data = response.read()
        else:
            infile = open(self.source)
            self.data = infile.read()
            infile.close()
        self.logger.debug("Loaded content for " + self.source)
    
    def getContent(self):
        '''
        Get the HTML content.
        '''
        return self.data
        
    def getDigitalObjectUrl(self):
        '''
        Get the URL to the digital object representation.
        '''
        soup = BeautifulSoup(self.data)
        try:
            thumbnail = soup.find('div',{'class':'image-caption'}).find('a').find('img')
            if thumbnail:
                url = thumbnail['src']
                if 'http' in url:
                    # absolute url reference
                    return url.encode("utf-8")
                else:
                    # relative url reference
                    pageurl = self.getUrl()
                    return urlparse.urljoin(pageurl,url).encode("utf-8")
        except:
            return None
        
    def getEacCpfUrl(self):
        '''
        Get the URL to the EAC-CPF alternate representation of this page.
        '''
        soup = BeautifulSoup(self.data)
        meta = soup.findAll('meta', {'name':'EAC'})
        try:
            # we need to deal with relative URLs in this reference
            # by appending the parent directory path
            return meta[0].get('content')
        except:
            return None

    def getFilename(self):
        '''
        Get the filename.
        '''
        url = self.getUrl()
        return self._getFileName(url)
    
    def getHtmlIndexContent(self):
        '''
        Extract HTML metadata and content for indexing.
        '''
        soup = BeautifulSoup(self.data)
        data = {}
        data['id'] = self.getRecordId()
        data['uri'] = self.getUrl()
        title = soup.find('title')
        if title:
            data['title'] = title.text.encode("utf-8")
        dctype = soup.find('meta',{'name':'DC.Type'})
        if dctype:
            data['type'] = dctype.text.encode("utf-8")
        # text
        texts = soup.findAll(text=True)
        visible_elements = [self._getVisibleText(elem) for elem in texts]
        data['abstract'] = ' '.join(visible_elements)
        return data
    
    def getRecordId(self):
        '''
        Get the record identifier for the record represented by the HTML page. 
        If the page does not have an identifier ID then None is returned.
        '''
        if self.hasEacCpfAlternate():
            uri = self.getUrl()
            filename = self._getFileName(uri)
            name = filename.split('.')
            return name[0]
        else: 
            return None
    
    def getUrl(self):
        '''
        Get the document URI. If a URI has been assigned to the document, then 
        use that as the default. If not, attempt to extract the DC.Identifier 
        value from the HTML meta tag. Return None if nothing is found.
        '''
        if hasattr(self, 'url'):
            return self.url
        else:
            soup = BeautifulSoup(self.data)
            meta = soup.findAll('meta', {'name':'DC.Identifier'})
            try:
                uri = meta[0].get('content')
                return uri.replace(' ','%20').encode("utf-8")
            except:
                return None
    
    def hasEacCpfAlternate(self):
        '''
        Determine if this page has an EAC-CPF alternate representation.
        '''
        soup = BeautifulSoup(self.data)
        meta = soup.findAll('meta', {'name':'EAC'})
        try:
            alt = meta[0].get('content')
            if alt:
                return True
            return False
        except:
            return False

    def hasRecord(self):
        '''
        Determine if the HTML page has a record.
        '''
        if self.getRecordId():
            return True
        return False
    
    def write(self, Path):
        '''
        Write data to the file in the specified path.
        '''
        outfile = open(Path + os.sep + self.getFilename(),'w')
        outfile.write(self.data)
        outfile.close()
        self.logger.info("Stored Html document " + self.getRecordId())
