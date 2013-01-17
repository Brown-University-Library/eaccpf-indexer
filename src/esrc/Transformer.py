'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from lxml import etree
import logging
import os
import re 
import yaml

class Transformer(object):
    '''
    Transforms an EAC file into a Solr Input Document.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('feeder')

    def _apply_doc_boost(self, doc, boost):
        '''
        Apply document boost value.
        '''
        if boost is not None:
            for b in boost:
                if re.search(b, self.document):
                    doc.xpath('//add/doc')[0].set("boost", str(boost[b]))

    def _apply_field_boosts(self, doc, boost):
        '''
        Apply field boost value.
        '''
        if boost is not None:
            for b in boost:
                searchfor = "//add/doc/field[@name='" + b + "']"
            try:
                doc.xpath(searchfor)[0].set("boost", str(boost[b]))
            except:
                pass

    def _getXMLFileName(self, filename):
        '''
        Takes a file name and returns a name with .yml appended.
        '''
        name, _ = os.path.splitext(filename)
        return name + ".xml"

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

    def mergeInferredDataIntoSID(self, source, output, report=None):
        '''
        Merge inference data into Solr Input Document.
        '''
        # confirm that the source_eac and output directories exist
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        # process files
        files = os.listdir(source)
        for filename in files:
            try:
                # read inferred data file
                infile = open(source + os.sep + filename,'r')
                data = yaml.load(infile)
                infile.close()
                # read output Solr document
                xmlFileName = self._getXMLFileName(filename)
                outfile = open(output + os.sep + xmlFileName, 'r+')
                xml = outfile.read()
                sid = etree.XML(xml)
                # add inferred fields
                
                # close the output file
                outfile.close()
                self.logger.info("Inferred data added to Solr Input Document " + filename)
            except Exception:
                self.logger.warning("Could not complete merge processing for " + filename, exc_info=True)
    
    def run(self, params):
        '''
        Execute transformation on EAC source document, then merge in inferred data.
        Write a valid Solr Input Document.
        '''
        self.logger.info("Starting transform operation")
        # get parameters
        output = params.get("transform","output")
        report = params.get("transform","report")
        source_eac = params.get("transform","input_eac")
        source_inferred = params.get("transform","input_inferred")
        transform = params.get("transform","transform")
        # create output folder
        self._makeCache(output)
        # execute initial transformation
        self.transformEACtoSID(source_eac, output, transform, report)
        self.mergeInferredDataIntoSID(source_inferred, output, report)
    
    def transformEACtoSID(self, source, output, xslt, report=None):
        '''
        Transform EAC document to Solr Input Document format using the
        specified XSLT transform file.
        '''
        # read the XSLT file
        try:
            xslt_file = open(xslt,'r')
            xslt_data = xslt_file.read()
            xslt_root = etree.XML(xslt_data)
            xslt_file.close()
            transform = etree.XSLT(xslt_root)
        except:
            self.logger.critical("Could not load XSLT file " + xslt)
        # confirm that the source and output directories exist
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        # process files
        files = os.listdir(source)
        for filename in files:
            try:
                # read source data
                infile = open(source + os.sep + filename, 'r')
                data = infile.read()
                infile.close()
                # create xml tree
                xml = etree.XML(data)
                # extract the @source and @referrer values
                source = 'http://example.com'
                referrer = 'http://example.com'
                # transform the source file
                result = transform(xml)
                # self._merge(solr_doc, eac_doc)
                # self._apply_doc_boost(solr_doc, config['boost-docs'])
                # self._apply_field_boosts(solr_doc, config['boost-fields'])
                # write the output file
                outfile = open(output + os.sep + filename, 'w')
                result.write(outfile, pretty_print=True, xml_declaration=True)
                outfile.close()
                self.logger.info("Transformed EAC to Solr Input Document " + filename)
            except Exception:
                self.logger.warning("Could not complete XSLT processing for " + filename, exc_info=True)
    