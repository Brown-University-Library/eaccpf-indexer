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
    Merge and transform source data to Solr Input Document format.
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
        Get document source and referrer URI values from 
        comment embedded in the document.
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
            
    def _removeNameSpaces(self, Text):
        '''
        ISSUE #4: When the XML/XSLT parser encounters a problem, it fails 
        silently and does not return any results. We've found that the 
        problem occurs due to namespace declarations in source files. 
        Because these are not important in the transformation to SID 
        format, we strip them out here before processing.
        '''
        for ns in re.findall("\w*:\w*=\".*\"", Text):
            Text = Text.replace(ns,'')
        for ns in re.findall("xmlns=\".*\"", Text):
            Text = Text.replace(ns,'')
        return Text

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
                # ISSUE #5 the geocoder can return multiple locations when an address is
                # not specific enough. Or, in some cases, a record has multiple events and
                # associated locations.  The Solr index allows for one location field entry, 
                # and multiple geohash entries.  Here, we use the first location as the 
                # primary record location, then make all subsequent locations geohashes.
                if 'locations' in inferred:
                    count = 0
                    for location in inferred['locations']:
                        # the first location in the list will become the 
                        # primary entity locaion
                        if count == 0:
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
                        else:
                            # all subsequent locations will be added to the loocation_geohash field
                            lat = location['coordinates'][0]
                            lng = location['coordinates'][1]
                            latlng = str(lat) + "," + str(lng)
                            coordinates = etree.Element('field', name='location_geohash')
                            coordinates.text = latlng
                            doc.append(coordinates)
                        # increment count
                        count = count + 1
                # @todo: add inferred entities
                if 'entities' in inferred:
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
                if 'relationship' in inferred:
                    pass
                # @todo: add inferred topics
                if 'topic' in inferred:
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
        Execute transformation on source document, then merge in inferred data.
        Write a valid Solr Input Document.
        '''
        # get parameters
        merge = params.get("transform","merge")
        output = params.get("transform","output")
        report = params.get("transform","report")
        source_inferred = params.get("transform","input_inferred")
        source_xml = params.get("transform","input_xml")
        xslt = params.get("transform","xslt")
        #schema = params.get("transform","schema")
        # create output folder
        self._makeCache(output)
        # transform to SID
        self.transformToSolrInputDocument(source_xml, output, xslt, report)
        # merge inferred data
        if merge.lower() == "true":
            self.mergeInferredDataIntoSID(source_inferred, output, report)
        # boost fields
        # validate output
        try:
            schema = params.get("transform","schema")
            self.validate(output, schema, report)
        except:
            self.logger.debug("No schema file specified")
    
    def transformToSolrInputDocument(self, source, output, xslt, report=None):
        '''
        Transform document to Solr Input Document format using the
        specified XSLT transform file.
        '''
        # check state
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        assert os.path.exists(xslt), self.logger.warning("Transform file does not exist: " + xslt)
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # load XSLT files
        try:
            xslt_file = open(xslt,'r')
            xslt_data = xslt_file.read()
            xslt_root = etree.XML(xslt_data)
            xslt_file.close()
            transform = etree.XSLT(xslt_root)
        except:
            self.logger.critical("Could not load XSLT file ")
        # process files
        files = os.listdir(source)
        for filename in files:
            try:
                # read source data
                infile = open(source + os.sep + filename,'r')
                data = infile.read()
                infile.close()
                # ISSUE #4: remove namespaces in the XML document before transforming
                data = self._removeNameSpaces(data)
                # create document tree
                xml = etree.XML(data)
                # transform the document
                result = transform(xml)
                # get the doc element
                sid = result.find('doc')
                # get the document source and referrer values from the embedded comment
                src_val, ref_val = self._getSourceAndReferrerValues(source + os.sep + filename)
                # append the source and referrer values to the SID
                if src_val:
                    src_field = etree.Element('field',name='source_uri')
                    src_field.text = src_val
                    sid.append(src_field)
                if ref_val:
                    ref_field = etree.Element('field',name='referrer_uri')
                    ref_field.text = ref_val
                    sid.append(ref_field)
                # write the output file
                outfile = open(output + os.sep + filename, 'w')
                result.write(outfile, pretty_print=True, xml_declaration=True)
                outfile.close()
                self.logger.info("Transformed document to Solr Input Document " + filename)
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
        # load schemas
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
                self.logger.warning("Document does not conform to schema " + filename)        
        