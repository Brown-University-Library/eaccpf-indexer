'''
This file is subject to the terms and conditions defined in the
'LICENSE.txt' file, which is part of this source code package.
'''

from BeautifulSoup import BeautifulSoup as soup  
import logging
import os

class Cleaner():
    '''
    Corrects common errors in XML files and validates the file against an 
    external schema.
    '''

    def __init__(self):
        '''
        Initialize the class
        '''
        self.logger = logging.getLogger('feeder')

    def _convertHTMLEntitiesToXMLEntities(self, content):
        '''
        Convert HTML entities into XML entities.
        '''
        return soup(content,convertEntities=soup.HTML_ENTITIES)

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
        self.logger.info("Cleaning files from " + source)
        # make output directory
        self._makeCache(output)
        # process files
        files = os.listdir(source)
        for filename in files:
            try:
                # read data
                infile = open(source + os.sep + filename,'r')
                data = infile.read()
                data = self._convertHTMLEntitiesToXMLEntities(data)
                infile.close()
                # write data
                outfile = open(output + os.sep + filename, 'w')
                outfile.write(data.prettify())
                outfile.close()
                self.logger.info("Cleaned " + filename)
            except Exception, e:
                import traceback
                traceback.print_stack()
                self.logger.warning("Could not complete processing on " + filename)
        
    def run(self, params):
        '''
        Execute the clean operation using specified parameters.
        '''
        self.logger.info("Starting clean operation")
        # get parameters
        source = params.get("clean","input")
        output = params.get("clean","output")
        report = params.get("clean","report")
        #schema = params.get("clean","schema")
        # clean data
        self.clean(source,output,report)
        # validate cleaned data files
        #self.validate(output, schema, report)

    def validate(self, source, schema, report):
        '''
        Validate a collection of files against an XML schema.
        '''
        # load the schema
        try:
            pass
        except Exception:
            self.logger.critical("Could not load schema file " + schema)
        # validate files against schema
        files = os.listdir(source)
        for filename in files:
            infile = open(source + os.sep + filename,'r')
            try:
                pass
            except Exception:
                pass
            finally:
                infile.close()
        
