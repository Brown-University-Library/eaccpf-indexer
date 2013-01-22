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

    def _getInferredDataFileName(self, filename):
        '''
        Takes a file name and returns a name with .yml appended.
        '''
        name, _ = os.path.splitext(filename)
        return name + ".yml"

    def _getSourceAndReferrerValues(self, filename):
        '''
        Get EAC document source and referrer URI values from 
        comment embedded in the EAC document.
        '''
        infile = open(filename,'r')
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
        # check state
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # for each solr input document
        files = os.listdir(output)
        for filename in files:
            try:
                # read Solr Input Document
                xml = etree.parse(output + os.sep + filename)
                root = xml.getroot()
                doc = root.getchildren()[0]
                # read inferred data file
                inferredFileName = self._getInferredDataFileName(filename)
                infile = open(source + os.sep + inferredFileName,'r+')
                data = infile.read()
                inferred = yaml.load(data)
                infile.close()
                # add inferred locations
                if inferred['locations']:
                    for location in inferred['locations']:
                        # address
                        address = etree.Element('field', name='address')
                        address.text = location['address']
                        doc.append(address)
                        # coordinates
                        lat = location['coordinates'][0]
                        lng = location['coordinates'][1]
                        latlng = str(lat) + "," + str(lng)
                        coordinates = etree.Element('field', name='location')
                        coordinates.text = latlng
                        doc.append(coordinates)
                        # latitude
                        location_0 = etree.Element('field', name='location_0_coordinate')
                        location_0.text = str(lat)
                        # longitude
                        doc.append(location_0)
                        location_1 = etree.Element('field', name='location_1_coordinate')
                        location_1.text = str(lng)
                        doc.append(location_1)
                # @todo: add inferred entities
                if inferred['entities']:
                    for entity in inferred['entities']:
                        if entity['type'] == 'City':
                            pass
                        elif entity['type'] == 'Concept':
                            pass
                        elif entity['type'] == 'Organization':
                            pass
                        elif entity['type'] == 'Person':
                            pass
                        elif entity['type'] == 'Region':
                            pass
                # @todo: add inferred relationships
                if inferred['relationship']:
                    pass
                # @todo: add inferred topics
                if inferred['topic']:
                    pass
                # write the updated file
                outfile = open(output + os.sep + filename,'w')
                xml.write(outfile, pretty_print=True, xml_declaration=True)
                outfile.close()
                self.logger.info("Merged inferred data into " + filename)
            except Exception:
                self.logger.warning("Could not complete merge processing for " + filename, exc_info=True)
    
    def run(self, params):
        '''
        Execute transformation on EAC source document, then merge in inferred data.
        Write a valid Solr Input Document.
        '''
        # get parameters
        merge = params.get("transform","merge")
        output = params.get("transform","output")
        report = params.get("transform","report")
        source_eac = params.get("transform","input_eac")
        source_inferred = params.get("transform","input_inferred")
        xslt = params.get("transform","xslt")
        schema = params.get("transform","schema")
        # create output folder
        self._makeCache(output)
        # transform EAC to SID
        self.transformEACtoSID(source_eac, output, xslt, report)
        # merge inferred data
        if merge.lower() == "true":
            self.mergeInferredDataIntoSID(source_inferred, output, report)
        # validate results
        # self.validate(output, schema, report)
    
    def transformEACtoSID(self, source, output, xslt, report=None):
        '''
        Transform EAC document to Solr Input Document format using the
        specified XSLT transform file.
        '''
        # check state
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        assert os.path.exists(xslt), self.logger.warning("XSLT file does not exist: " + xslt)
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # read the XSLT file
        try:
            xslt_file = open(xslt,'r')
            xslt_data = xslt_file.read()
            xslt_root = etree.XML(xslt_data)
            xslt_file.close()
            transform = etree.XSLT(xslt_root)
        except:
            self.logger.critical("Could not load XSLT file " + xslt)
        # process files
        files = os.listdir(source)
        for filename in files:
            try:
                # read source data
                xml = etree.parse(source + os.sep + filename)
                # transform the source file
                result = transform(xml)
                # get the doc element
                doc = result.find('doc')
                # get the EAC document source and referrer values
                # from the comment embedded at the end of the EAC
                src_val, ref_val = self._getSourceAndReferrerValues(source + os.sep + filename)
                # append the source and referrer values to the SID
                if src_val:
                    src_field = etree.Element('field',name='source_uri')
                    src_field.text = src_val
                    doc.append(src_field)
                if ref_val:
                    ref_field = etree.Element('field',name='referrer_uri')
                    ref_field.text = ref_val
                    doc.append(ref_field)
                # write the output file
                outfile = open(output + os.sep + filename, 'w')
                result.write(outfile, pretty_print=True, xml_declaration=True)
                outfile.close()
                self.logger.info("Transformed EAC to Solr Input Document " + filename)
            except Exception:
                self.logger.warning("Could not complete XSLT processing for " + filename, exc_info=True)
                
    def validate(self, source, schema, report=None):
        '''
        Validate a collection of files against an XML schema.
        '''
        # check state
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(schema), self.logger.warning("Schema file does not exist: " + schema)
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # load schema 
        try:
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
                self.logger.warning("Document does not conform to solr Input Document schema " + filename)        
        