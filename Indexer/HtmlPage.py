"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from lxml import etree

import Cfg
import Utils
import codecs
import hashlib
import logging
import lxml.html
import os
import re
import urlparse


class HtmlPage(object):
    """
    An HTML document conforming to ESRC OHRM standards.
    """

    def __init__(self, source, filename=None, base_url=None):
        """
        :param source: file system path to the document or its parent folder
        :param filename: document filename
        :param base_url: override the document URL value by specifying the
         base of the document's public URL. The document URL value then
         becomes the concatenation of the base URL and the document file name.
        """
        self.log = logging.getLogger()
        self.base = base_url
        if filename:
            self.filename = filename
            self.parent_path = source
            self.source = source + os.sep + filename
        else:
            self.filename = Utils.getFileName(source)
            self.parent_path = os.path.dirname(source)
            self.source = source
        # load data
        self.data = Utils.load_from_source(self.source)
        self.tree = lxml.html.parse(self.source) # @todo should probably use self.data as input instead of parsing a path

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
            thumbnail_url = thumbnail[0].attrib['src']
            if 'http' in thumbnail_url:
                # absolute url reference
                return str(thumbnail_url)
            else:
                # relative url reference
                page_url = self.getUrl()
                return str(urlparse.urljoin(page_url, thumbnail_url))
        except:
            self.log.debug("Digital object URL not found in {0}".format(self.filename), exc_info=Cfg.LOG_EXC_INFO)

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
        Extract HTML metadata and content for indexing. Downstream data
        processing will break if any of the values are null.
        """
        data = {}
        _id = self.getRecordId()
        _title = self.getTitle()
        _type = self.getType()
        _text = self.getText()
        data['id'] = _id if _id is not None else self.getFilename()
        data['presentation_url'] = self.getUrl()
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

    def getText(self, include_head_metadata=False):
        """
        Get body text with tags, comments and Javascript stripped out.
        """
        # strip all script nodes from the document
        for node in self.tree.xpath("//script"):
            parent = node.getparent()
            if parent is not None:
                parent.remove(node)
        # strip all comment nodes from the document
        for node in self.tree.xpath("//comment()"):
            parent = node.getparent()
            if parent is not None:
                parent.remove(node)
        # get the text content of the page
        if include_head_metadata:
            text = etree.tostring(self.tree)
        else:
            body = self.tree.xpath("//body/*")
            text = ""
            for t in body:
                text += t.text_content()
        # strip tags and control chars
        text = re.sub('<[^<]+?>', '', text)
        text = re.sub('[\r|\n|\t]', ' ', text)
        # replace encoded characters
        text = re.sub('&#[0-9]*;', ' ', text)
        text = re.sub('&(amp|nbsp|copy);', ' ', text)
        # remove extraneous whitespace
        tokens = text.split()
        text = ' '.join(tokens)
        return text

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
        Determine the public document URL from the data that has been provided.
        """
        # if the source is a URL then use that
        if 'http://' in self.source or 'https://' in self.source:
            return self.source
        # else, if a base url has been specified, then construct the public URL
        # from the combination of the base url and the document file name
        elif self.base and not self.base.endswith('/'):
            return self.base + '/' + self.filename
        elif self.base:
            return self.base + self.filename
        else:
            # if all else fails, try to get the URL from the DC.Identifier
            # value in the document HEAD
            try:
                tags = self.tree.findall('//meta')
                for tag in tags:
                    if 'name' in tag.attrib and tag.attrib['name'] == 'DC.Identifier':
                        uri = tag.attrib['content']
                        return uri.replace(' ','%20')
            except:
                pass

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

    def write(self, Path, Filename=None):
        """
        Write document to the specified path.
        """
        filename = Filename if Filename else self.filename
        output_path = Path + filename if Path.endswith('/') else Path + os.sep + filename
        with open(output_path, 'w') as f:
            f.write(self.data)
        self.log.info("Stored HTML document {0}".format(filename))
