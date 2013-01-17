'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

#from BeautifulSoup import BeautifulSoup as soup  
from lxml import etree
import htmlentitydefs
import logging
import os
import re

class Cleaner():
    '''
    Corrects common errors in XML files and validates the file against an 
    external schema.
    
    @todo: Need to replace BeautifulSoup in any kind of write situation because it changes the case of tag names and attributes
    '''

    def __init__(self):
        '''
        Initialize the class
        '''
        self.logger = logging.getLogger('feeder')

    def _convertHTMLEntitiesToXMLEntities(self, text):
        '''
        Convert HTML entities into XML entities.
        @see http://effbot.org/zone/re-sub.htm#unescape-html
        '''
        def fixup(m):
            text = m.group(0)
            if text[:2] == "&#":
                # character reference
                try:
                    if text[:3] == "&#x":
                        return unichr(int(text[3:-1], 16))
                    else:
                        return unichr(int(text[2:-1]))
                except ValueError:
                    pass
            else:
                # named entity
                try:
                    text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
                except KeyError:
                    pass
            return text # leave as is
        return re.sub("&#?\w+;", fixup, text)

    def _convertDateFieldsToISO(self,xml):
        '''
        Convert dates into ISO format. Where a date is specified with a circa 
        indication, or 's to indicate a decade, expand the date into a range.
        @todo: finish implementing this method
        '''
        pass
    
    def _convertUnescapedAttributeURL(self,xml):
        '''
        Where an XML tag contains an attribute with a URL in it, any 
        ampersand characters in the URL must be escaped.
        @todo: finish implementing this method
        @see http://priyadi.net/archives/2004/09/26/ampersand-is-not-allowed-within-xml-attributes-value/
        '''
        pass

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

    def clean(self, source, output, report):
        '''
        Clean all files in source directory and write them to the output 
        directory. If the source and output are the same directory, the
        source files will be overwritten.  
        '''
        self.logger.info("Cleaning files in " + source)
        # make output directory
        self._makeCache(output)
        # process files
        files = os.listdir(source)
        for filename in files:
            try:
                # read data
                infile = open(source + os.sep + filename,'r')
                data = infile.read()
                infile.close()
                # fix common errors
                data = self._convertHTMLEntitiesToXMLEntities(data)
                data = self._convertUnescapedAttributeURL(data)
                data = self._convertDateFieldsToISO(data)
                # write data
                outfile = open(output + os.sep + filename, 'w')
                outfile.write(data)
                outfile.close()
                self.logger.info("Cleaned " + filename)
            except Exception:
                import traceback
                traceback.print_stack()
                self.logger.warning("Could not complete processing on " + filename)
        
    def run(self, params):
        '''
        Execute the clean operation using specified parameters.
        '''
        # get parameters
        source = params.get("clean","input")
        output = params.get("clean","output")
        report = params.get("clean","report")
        # clean data
        self.clean(source,output,report)
        # validate cleaned data files
        try:
            schema = params.get("clean","schema")
            self.validate(output, schema, report)
        except:
            self.logger.debug("No schema file specified")

    def validate(self, source, schema, report):
        '''
        Validate a collection of files against an XML schema.
        '''
        self.logger.info("Validating files in " + source)
        try:
            # load schema file
            infile = open(schema, 'r')
            schema_data = infile.read()
            schema_root = etree.XML(schema_data) 
            schema = etree.XMLSchema(schema_root)
            infile.close()
            self.logger.info("Loaded schema file " + schema)
        except Exception:
            self.logger.critical("Could not load schema file " + schema)
        # create validating parser
        parser = etree.XMLParser(schema=schema)
        # validate files against schema
        files = os.listdir(source)
        for filename in files:
            infile = open(source + os.sep + filename,'r')
            data = infile.read()
            infile.close()
            try:
                etree.fromstring(data, parser)
            except Exception:
                self.logger.warning("Document does not conform to schema " + filename)        
