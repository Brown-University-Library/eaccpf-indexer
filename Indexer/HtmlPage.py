"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

try:
    from bs4 import BeautifulSoup as bs4
except:
    from BeautifulSoup import BeautifulSoup as bs4
import hashlib
import logging
import os
import re
import urllib2
import urlparse


class HtmlPage(object):
    """
    HTML document pages contain metadata and references to external entities
    that are the subject of indexing. This class wraps the HTML document and
    provides convenience methods for extracting required metadata.
    """

    def __init__(self, Source, BaseUrl=None, Data=None):
        """
        Source is a file system path or URL to the document. URL is an 
        optional argument specified when the document is being indexed from a 
        file system, and is used to determine what the file's public URL should
        be. If the document contains absolute URLs, then the URL parameter is 
        ignored.
        """
        self.logger = logging.getLogger('HtmlPage')
        self.source = Source
        if Data:
            self.data = Data
        else:
            self.data = self._load(self.source)
        self.soup = bs4(self.data)
        if BaseUrl:
            if not BaseUrl.endswith('/'):
                BaseUrl = BaseUrl + '/'
            filename = self._getFileName(Source)        
            self.url = BaseUrl + filename

    def _getAbsoluteUrl(self,Base,Path):
        """
        Get the absolute URL for a path.
        """
        url = urlparse.urljoin(Base,Path)
        return url.replace(' ','%20')
        
    def _getDocumentParentPath(self, Path):
        """
        Get the path to the parent of the specified directory.
        """
        i = Path.rfind('/')
        return Path[:i+1]

    def _getDocumentParentUri(self, Uri):
        """
        Get the parent directory of the file in the specified URL.  Non / 
        terminated URLs are treated as representing files.
        """
        uri = self.getUrl()
        i = uri.rfind('/')
        url = uri[:i+1]
        return url.replace(' ','%20').encode("utf-8")

    def _getFileName(self, Url):
        """
        Get the filename from the specified URI or path.
        """
        if "/" in Url:
            parts = Url.split("/")
            return parts[-1]
        return Url

    def _getTagAttributeValueByName(self, Tags, Type, Attribute):
        """l
        Get the value of the specified digital object field name from a list of
        tags. Return None if the field name can not be found.
        """
        for tag in Tags:
            field = tag.find(Type)
            if field:
                val = field[Attribute]
                return val.encode("utf8")
        return None

    def _getTagContentByClass(self, Tags, Type, FieldName, Field='class'):
        """
        Get the value of the specified digital object field name from a list of
        tags. Return None if the field name can not be found.
        """
        for tag in Tags:
            field = tag.find(Type,{Field:FieldName})
            if field:
                return field.text.encode("utf8")
        return None
    
    def _getVisibleText(self, element):
        """Remove all markup from the element text content and return the text.
        """
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return ''
        result = re.sub('<!--.*-->|\r|\n', '', str(element), flags=re.DOTALL)
        result = re.sub('\s{2,}|&nbsp;', ' ', result)
        return result

    def _load(self, Source):
        """
        Load the document content.
        """
        try:
            if 'http://' in Source or 'https://' in Source:
                response = urllib2.urlopen(Source)
                return response.read()
            else:
                infile = open(Source)
                data = infile.read()
                infile.close()
                return data
        except:
            return None

    def getContent(self):
        """
        Get the HTML content.
        """
        return self.data
        
    def getDigitalObjectUrl(self):
        """
        Get the URL to the digital object representation.
        """
        try:
            thumbnail = self.soup.find('div',{'class':'image-caption'}).find('a').find('img')
            if thumbnail:
                url = thumbnail['src']
                if 'http' in url:
                    # absolute url reference
                    return str(url)
                else:
                    # relative url reference
                    pageurl = self.getUrl()
                    return str(urlparse.urljoin(pageurl,url))
        except:
            return None
        
    def getEacCpfUrl(self):
        """
        Get the URL to the EAC-CPF alternate representation of this page.
        """
        meta = self.soup.findAll('meta', {'name':'EAC'})
        try:
            # we need to deal with relative URLs in this reference
            # by appending the parent directory path
            return str(meta[0].get('content'))
        except:
            return None

    def getFilename(self):
        """
        Get the filename.
        """
        url = self.getUrl()
        return self._getFileName(url)

    def getHash(self):
        """
        Get a secure hash for the content in hexadecimal format.
        """
        h = hashlib.sha1()
        h.update(self.data)
        return h.hexdigest()

    def getHtmlIndexContent(self):
        """
        Extract HTML metadata and content for indexing.
        """
        data = {}
        data['id'] = self.getRecordId()
        data['uri'] = self.getUrl()
        try:
            title = self.soup.find('title')
            if title:
                data['title'] = title.text.encode("utf-8")
        except:
            data['title'] = ''
        dctype = self.soup.find('meta',{'name':'DC.Type'})
        if dctype:
            data['type'] = dctype.text.encode("utf-8")
        # text
        try:
            texts = self.soup.findAll(text=True)
            visible_elements = [self._getVisibleText(elem) for elem in texts]
            data['abstract'] = ' '.join(visible_elements)
        except:
            data['abstract'] = re.sub('<[^<]+?>', '', self.data)
            # msg = 'Could not extract text content for record {0}'.format(self.id)
            # raise Exception(msg)
        return data
    
    def getRecordId(self):
        """
        Get the record identifier for the record represented by the HTML page. 
        If the page does not have an identifier ID then None is returned.
        """
        uri = self.getUrl()
        filename = self._getFileName(uri)
        name = filename.split('.')
        return name[0]

    def getUrl(self):
        """
        Get the document URI. If a URI has been assigned to the document, then 
        use that as the default. If not, attempt to extract the DC.Identifier 
        value from the HTML meta tag. Return None if nothing is found.
        """
        if hasattr(self, 'url'):
            return self.url
        else:
            meta = self.soup.findAll('meta', {'name':'DC.Identifier'})
            try:
                uri = meta[0].get('content')
                return uri.replace(' ','%20').encode("utf-8")
            except:
                return None
    
    def hasEacCpfAlternate(self):
        """
        Determine if this page has an EAC-CPF alternate representation.
        """
        meta = self.soup.findAll('meta', {'name':'EAC'})
        try:
            alt = meta[0].get('content')
            if alt:
                return True
            return False
        except:
            return False

    def hasRecord(self):
        """
        Determine if the HTML page has a record.
        """
        if self.getRecordId():
            return True
        return False
    
    def write(self, Path):
        """
        Write data to the file in the specified path.
        """
        outfile = open(Path + os.sep + self.getFilename(),'w')
        outfile.write(str(self.data))
        outfile.close()
        record = self.getRecordId()
        if record:
            self.logger.info("Stored HTML document " + record)
        else:
            self.logger.info("Stored HTML document " + self.getFilename())
