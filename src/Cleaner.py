'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from BeautifulSoup import BeautifulSoup
from lxml import etree

import htmlentitydefs
import logging
import os
import re

class Cleaner():
    '''
    Corrects common errors in XML files and validates the file against an 
    external schema.
    '''

    def __init__(self):
        '''
        Initialize the class
        '''
        self.logger = logging.getLogger('Cleaner')
        
    def _convertHTMLEntitiesToUnicode(self, text):
        '''
        Converts HTML entities to unicode.  For example '&amp;' becomes '&'.
        '''
        text = unicode(BeautifulSoup(text, convertEntities=BeautifulSoup.ALL_ENTITIES))
        return text    

    def _fixAttributeURLEncoding(self,xml):
        '''
        Where an XML tag contains an attribute with a URL in it, any 
        ampersand characters in the URL must be escaped.
        @todo: finish implementing this method
        @see http://priyadi.net/archives/2004/09/26/ampersand-is-not-allowed-within-xml-attributes-value/
        '''
        return xml

    def _fixDateFields(self,xml):
        '''
        Convert dates into ISO format. Where a date is specified with a circa 
        indication, or 's to indicate a decade, expand the date into a range.
        @todo: finish implementing this method
        '''
        return xml
   
    def _fixEntityReferences(self, Text):
        '''
        Convert HTML entities into XML entities.
        @see http://effbot.org/zone/re-sub.htm#unescape-html
        '''
        def fixup(m):
            Text = m.group(0)
            if Text[:2] == "&#":
                # character reference
                try:
                    if Text[:3] == "&#x":
                        return unichr(int(Text[3:-1], 16))
                    else:
                        return unichr(int(Text[2:-1]))
                except ValueError:
                    pass
            else:
                # named entity
                try:
                    Text = unichr(htmlentitydefs.name2codepoint[Text[1:-1]])
                except KeyError:
                    pass
            return Text # leave as is
        return re.sub("&#?\w+;", fixup, Text)

    def _getSourceAndReferrerValues(self, Path):
        '''
        Get source and referrer URI values from comment embedded in the document.
        '''
        infile = open(Path,'r')
        lines = infile.readlines()
        infile.close()
        # process lines
        for line in lines:
            try:
                src = line.index("@source")
                ref = line.index("@referrer")
                source = line[src+len("@source="):ref-1]
                referrer = line[ref+len("@referrer="):-4]
                if not referrer.startswith("http"):
                    referrer = None
                return (source, referrer)
            except:
                pass
        # default case
        return ('', '')
    
    def _isEacCpf(self, Path):
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
    
    def _isHtml(self, Path):
        '''
        Determine if the file at the specified path is HTML.
        '''
        if Path.endswith("htm") or Path.endswith("html"):
            infile = open(Path,'r')
            data = infile.read()
            infile.close()
            if "<html" in data.lower():
                return True
        return False

    def _makeCache(self, path):
        '''
        Create a cache folder at the specified path if none exists.
        If the path already exists, delete all files.
        '''
        if not os.path.exists(path):
            os.makedirs(path)
            self.logger.info("Created output folder at " + path)
        else:
            files = os.listdir(path)
            for afile in files:
                os.remove(path + os.sep + afile)
            self.logger.info("Cleared output folder at " + path)
    
    def _removeEmptyDateFields(self, Text):
        '''
        Remove any empty fromDate or toDate tags.
        '''
        xml = etree.XML(Text)
        tree = etree.ElementTree(xml)
        for item in tree.findall('//fromDate'):
            if item.text is None or item.text == '':
                item.getparent().remove(item)
        for item in tree.findall('//toDate'):
            if item.text is None or item.text == '':
                item.getparent().remove(item)
        return etree.tostring(xml,pretty_print=True)
    
    def _removeEmptyStandardDateFields(self, Text):
        '''
        Remove any fromDate or toDate tags that have empty standardDate attributes.
        '''
        xml = etree.XML(Text)
        tree = etree.ElementTree(xml)
        for item in tree.findall('//fromDate'):
            date = item.attrib['standardDate']
            if date is None or date == '':
                item.attrib.pop('standardDate')
        for item in tree.findall('//toDate'):
            date = item.attrib['standardDate']
            if date is None or date == '':
                item.attrib.pop('standardDate')
        return etree.tostring(xml,pretty_print=True)
    
    def _removeSpanTags(self, Text):
        '''
        Remove all <span> and </span> tags from the markup.
        '''
        # replace simple cases first
        Text = Text.replace("<span>","")
        Text = Text.replace("</span>","")
        # replace spans with attributes
        for span in re.findall("<span \w*=\".*\">",Text):
            Text = Text.replace(span,'')
        return Text

    def clean(self, Source, Output):
        '''
        Read all files from source directory, apply fixes to common errors in 
        documents. Write cleaned files to the output directory.
        '''
        files = os.listdir(Source)
        for filename in files:
            try:
                # read data
                infile = open(Source + os.sep + filename,'r')
                data = infile.read()
                infile.close()        
                # fix problems
                if self._isEacCpf(Source + os.sep + filename):
                    # the source/referrer values comment gets deleted by the XML 
                    # parser, so we'll save it here temporarily while we do our cleanup
                    src, ref = self._getSourceAndReferrerValues(Source + os.sep + filename)
                    data = self.fixEacCpf(data)
                    # write source/referrer comment back at the end of the file
                    data += '\n<!-- @source=%(source)s @referrer=%(referrer)s -->' % {"source":src, "referrer":ref}
                elif self._isHtml(Source + os.sep + filename):
                    data = self.fixHtml(data)
                else:
                    pass
                # write data to specified file in the output directory.
                outfile_path = Output + os.sep + filename
                outfile = open(outfile_path,'w')
                outfile.write(data)
                outfile.close()
                self.logger.info("Stored document " + filename)
            except Exception:
                self.logger.warning("Could not complete processing on " + filename, exc_info=True)
        
    def fixEacCpf(self, Data):
        '''
        Clean problems that are typical of EAC-CPF files.
        '''
        # data = self._fixEntityReferences(data)
        data = self._fixAttributeURLEncoding(Data)
        data = self._fixDateFields(data)
        data = self._removeSpanTags(data)
        data = self._removeEmptyDateFields(data)
        data = self._removeEmptyStandardDateFields(data) # XML needs to be valid before we can do this
        return data
    
    def fixHtml(self, Data):
        '''
        Clean typical problems found in HTML files.
        '''
        data = self._convertHTMLEntitiesToUnicode(Data)
        return data
    
    def run(self, Params):
        '''
        Execute the clean operation using specified parameters.
        '''
        # get parameters
        source = Params.get("clean","input")
        output = Params.get("clean","output")
        # make output directory
        self._makeCache(output)
        # check state
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        # clean data
        self.clean(source,output)
        # validate cleaned data files
        try:
            schema = Params.get("clean","schema")
            self.validate(output,schema)
        except:
            self.logger.debug("No schema file specified")

    def validate(self, Source, Schema):
        '''
        Validate a collection of files against an XML schema.
        '''
        # check state
        assert os.path.exists(Source), self.logger.warning("Source path does not exist: " + Source)
        assert os.path.exists(Schema), self.logger.warning("Schema file does not exist: " + Schema)
        # load schema file
        try:
            infile = open(Schema, 'r')
            schema_data = infile.read()
            schema_root = etree.XML(schema_data)
            xmlschema = etree.XMLSchema(schema_root)
            infile.close()
            self.logger.info("Loaded schema file " + Schema)
        except Exception:
            self.logger.critical("Could not load schema file " + Schema)
        # create validating parser
        parser = etree.XMLParser(schema=xmlschema)
        # validate files against schema
        self.logger.info("Validating documents against schema")
        files = os.listdir(Source)
        for filename in files:
            infile = open(Source + os.sep + filename,'r')
            data = infile.read()
            infile.close()
            try:
                etree.fromstring(data, parser)
            except Exception:
                self.logger.warning("Document " + filename + " does not conform to schema")
