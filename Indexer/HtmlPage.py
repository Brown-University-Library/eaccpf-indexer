"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

import Cfg
import Utils
import codecs
import hashlib
import logging
import lxml.html
import os
import re
import urllib2
import urlparse


class HtmlPage(object):
    """
    HTML document pages contain metadata and references to external entities
    that are the subject of indexing. This class wraps the HTML document and
    provides convenience methods for extracting required metadata.

    The physical file system needs to mirror the public URLs, otherwise this
    module will provide erroneous URLs.

    @todo consider deferred loading of HTML content
    """

    def __init__(self, Source, BaseUrl=None):
        """
        Source is a file system path or URL to the document. BaseUrl is an
        optional argument specified when the document is being indexed from a 
        file system, and is used to determine what the file's public URL should
        be. If the document contains absolute URLs, then the BaseUrl parameter
        is ignored.
        """
        self.log = logging.getLogger()
        self.base = BaseUrl
        self.data = self._load(Source)
        self.filename = Utils.getFileName(Source)
        self.source = Source
        self.tree = lxml.html.parse(Source)
        self.url = self._getUrl()

    def _getAbsoluteUrl(self,Base,Path):
        """
        Get the absolute URL for a path.
        """
        url = urlparse.urljoin(Base, Path)
        return url.replace(' ','%20')
        
    def _getDocumentParentPath(self, Path):
        """
        Get the path to the parent of the specified directory.
        """
        i = Path.rfind('/')
        return Path[:i+1]

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
                return str(val)
        return None

    def _getTagContentByClass(self, Tags, Type, FieldName, Field='class'):
        """
        Get the value of the specified digital object field name from a list of
        tags. Return None if the field name can not be found.
        """
        for tag in Tags:
            field = tag.find(Type,{Field:FieldName})
            if field:
                return str(field.text)
        return None

    def _getUrl(self):
        """
        Determine the public document URL from the data that has been provided.
        If a source URI has been assigned to the document, then use that as the
        default. If not, attempt to extract the DC.Identifier value from the
        HTML meta tag. If that is not available, use the base URL value plus
        file name.
        """
        # if the source is a URL then use that
        if 'http://' in self.source or 'https://' in self.source:
            return self.source
        # try to get the URL from the DC.Identifier value in the document
        try:
            tags = self.tree.findall('//meta')
            for tag in tags:
                if 'name' in tag.attrib and tag.attrib['name'] == 'DC.Identifier':
                    uri = tag.attrib['content']
                    return uri.replace(' ','%20')
        except:
            pass
        # else, construct it from the base value + filename
        if self.base and not self.base.endswith('/'):
            return self.base + '/' + self.filename
        if self.base:
            return self.base + self.filename
        # the fall back is the use the filename
        return self.filename

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
        if 'http://' in Source or 'https://' in Source:
            response = urllib2.urlopen(Source)
            data = response.read()
            return unicode(data, errors='replace')
        else:
            with open(Source, 'r') as f:
                data = f.read()
                return unicode(data, errors='replace')

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
            thumbnail = self.tree.findall("//img[@id='dothumb']")
            url = thumbnail[0].attrib['src']
            if 'http' in url:
                # absolute url reference
                return str(url)
            else:
                # relative url reference
                pageurl = self.getUrl()
                return str(urlparse.urljoin(pageurl,url))
        except:
            self.log.debug("Digital object not found in {0}".format(self.url), exc_info=Cfg.LOG_EXC_INFO)
        return None

    def getEacCpfUrl(self):
        """
        Get the URL to the EAC-CPF alternate representation of this page.
        """
        tags = self.tree.findall('//meta')
        for tag in tags:
            if 'name' in tag.attrib and tag.attrib['name'] == 'EAC':
                return tag.attrib['content']

    def getFilename(self):
        """
        Get the filename.
        """
        return self.filename

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
        _id = self.getRecordId()
        _uri = self.getUrl()
        _title = self.getTitle()
        _type = self.getType()
        _text = self.getText()
        data['id'] = '' if _id is None else _id
        data['presentation_url'] = '' if _uri is None else _uri
        data['title'] = '' if _title is None else _title
        data['type'] = '' if _type is None else _type
        data['abstract'] = '' if _text is None else _text
        return data
    
    def getRecordId(self):
        """
        Return a record identifier for the page if the page represents an
        EAC-CPF entity. Return None otherwise.
        """
        if self.hasEacCpfAlternate():
            return Utils.getRecordIdFromFilename(self.filename)
        return None

    def getText(self):
        """
        Get body text with tags stripped out.
        """
        text = re.sub('<[^<]+?>', '', self.data)
        text = text.replace('\r\n', ' ')
        return text.replace('\t', ' ')

    def getTitle(self):
        """
        Get the document title.
        """
        # ISSUE #30 in some cases, the title string contains markup in it,
        # which results in only a portion of the title string being
        # returned. Here we concat the text content of all the child nodes
        # together to create a single title string
        title = ''
        title_elements = self.tree.xpath("//title")
        for t in title_elements.pop().itertext():
            title += t
        return title

    def getType(self):
        """
        Get the record entity type.
        """
        tags = self.tree.findall('//meta')
        for tag in tags:
            if 'name' in tag.attrib and tag.attrib['name'] == 'DC.Type':
                return tag.attrib['content']

    def getUrl(self):
        """
        Get the document URI.
        """
        if self.base:
            parsed = urlparse.urlparse(self.url)
            base = urlparse.urlparse(self.base)
            path = "{0}/{1}".format(base.path, parsed.path)
            path = re.sub("///", "/", path)
            path = re.sub("//", "/", path)
            return urlparse.urljoin(self.base, path)
        return self.url

    def hasEacCpfAlternate(self):
        """
        Determine if this page has an EAC-CPF alternate representation.
        """
        return True if self.getEacCpfUrl() else False

    def hasRecord(self):
        """
        Determine if the HTML page has a record.
        """
        return True if self.getRecordId() else False

    def write(self, Path):
        """
        Write document to the specified path.
        """
        outfile = codecs.open(Path + os.sep + self.getFilename(), 'w', 'utf-8')
        outfile.write(self.data)
        outfile.close()
        self.log.info("Stored HTML document {0}".format(self.filename))
