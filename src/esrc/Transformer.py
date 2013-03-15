'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from HtmlPage import HtmlPage
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
        self.logger = logging.getLogger('Transformer')

    def _applyFieldBoost(self, doc, boost):
        '''
        Apply field boost on the specified document.
        '''
        if boost is not None:
            for b in boost:
                searchfor = "//add/doc/field[@name='" + b + "']"
            try:
                doc.xpath(searchfor)[0].set("boost", str(boost[b]))
            except:
                pass

    def _boostFields(self, Path, FieldName, BoostValue):
        '''
        Boost the specified field for all Solr Input Document in the specified 
        path.
        '''
        assert os.path.exists(Path), self.logger.warning("Source documents path does not exist: " + Path)
        files = os.listdir(Path)
        for filename in files:
            if self._isSolrInputDocument(Path + os.sep + filename):
                pass

    def _getFileName(self, Filename):
        '''
        Get the filename from the specified URI or path.
        '''
        if "/" in Filename:
            parts = Filename.split("/")
            return parts[-1]
        return Filename

    def _getSourceAndReferrerValues(self, filename):
        '''
        Get document source and referrer URI values from the comment embedded 
        at the end of the document.
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
    
    def _isDigitalObjectYaml(self, Path):
        '''
        Determines if the file at the specified path is an image record in
        YAML format.
        '''
        if Path.endswith("yml"):
            infile = open(Path,'r')
            data = infile.read()
            infile.close()
            if "DIGITAL OBJECT record" in data:
                return True
        return False

    def _isEACCPF(self, Path):
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
    
    def _isInferredYaml(self, Path):
        '''
        Determines if the file at the specified path is an inferred data
        record in YAML format.
        '''
        if Path.endswith("yml"):
            infile = open(Path,'r')
            data = infile.read()
            infile.close()
            if "INFERRED DATA record" in data:
                return True
        return False
    
    def _isSolrInputDocument(self, Path):
        '''
        Determines if the file at the specified path is a Solr Input
        Document.
        '''
        if Path.endswith("xml"):
            infile = open(Path,'r')
            data = infile.read()
            infile.close()
            if "<add>" in data and "<doc>" in data:
                return True
        return False

    def _makeCache(self, Path):
        '''
        Create a cache folder at the specified Path if none exists.
        If the Path already exists, delete all files.
        '''
        if not os.path.exists(Path):
            os.makedirs(Path)
            self.logger.info("Created output folder at " + Path)
        else:
            files = os.listdir(Path)
            for afile in files:
                os.remove(Path + os.sep + afile)
            self.logger.info("Cleared output folder at " + Path)
            
    def _removeNameSpaces(self, Text):
        '''
        Remove namespace references from XML data.
        
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

    def mergeInferredRecordIntoSID(self, source, output, report=None):
        '''
        Merge inferred data into Solr Input Document. Write merged data to 
        output.
        '''
        try:
            # read input (inferred) data file
            infile = open(source,'r')
            data = infile.read()
            inferred = yaml.load(data)
            infile.close()
            if not os.path.exists(output):
                self.logger.warning("Output path does not exist " + output)
            else:
                # read output (Solr Input Document) data file
                xml = etree.parse(output)
                root = xml.getroot()
                doc = root.getchildren()[0]
                filename = self._getFileName(output)
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
                            # city
                            city = etree.Element('field', name='city')
                            city.text = location['primary_city']
                            doc.append(city)
                            # state
                            region = etree.Element('field', name='region')
                            region.text = location['primary_region']
                            doc.append(region)
                            # region
                            country = etree.Element('field', name='country')
                            country.text = location['primary_country']
                            doc.append(country)
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
    
    def mergeInferredRecordsIntoSID(self, sources, output, report=None):
        '''
        Transform zero or more paths with inferred object records to Solr Input 
        Document format.
        '''
        for source in sources:
            files = os.listdir(source)
            for filename in files:
                if self._isInferredYaml(source + os.sep + filename):
                    # get the name of the output record
                    self.mergeInferredRecordIntoSID(filename, output, report)
    
    def run(self, params):
        '''
        Execute transformations on source documents as specified. Write results 
        to the output path.
        '''
        # get parameters
        actions = params.get("transform","actions").split(',')
        boosts = params.get("transform","boost").split(',')
        output = params.get("transform","output")
        report = params.get("transform","report")
        sources = params.get("transform","sources").split(',')
        xslt = params.get("transform","xslt")
        # check state
        for source in sources:
            assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # create output folder
        self._makeCache(output)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        # execute actions
        for action in actions:
            if action == "html-to-sid":
                self.transformHtmlsToSid(sources, output, report)
            elif action == "eaccpf-to-sid":
                # create document transform
                assert os.path.exists(xslt), self.logger.warning("Transform path does not exist: " + xslt)
                try:
                    xslt_file = open(xslt,'r')
                    xslt_data = xslt_file.read()
                    xslt_root = etree.XML(xslt_data)
                    xslt_file.close()
                    transform = etree.XSLT(xslt_root)
                except:
                    self.logger.critical("Could not load XSLT file ")
                self.transformEACCPFsToSID(sources, output, transform, report)
            elif action == "digitalobject-to-sid":
                self.transformDigitalObjectsToSIDamlToSID(sources, output, report)
            elif action == "merge-inferred-into-sid":
                self.mergeInferredRecordsIntoSID(sources, output, report)
            else:
                self.logger.warning("Transform action is not available: " + action)
        # boost fields
        for boost in boosts:
            fieldname, boostval = boost.split(':')
            self._boostFields(output, fieldname, boostval)
        # validate output
        try:
            schema = params.get("transform","schema")
            self.validate(output, schema, report)
        except:
            self.logger.debug("No schema file specified")
    
    def transformDigitalObjectsToSID(self, sources, output, report=None):
        '''
        Transform zero or more paths with digital object YAML records to Solr 
        Input Document format.
        '''
        for source in sources:
            files = os.listdir(source)
            for filename in files:
                if self._isDigitalObjectYaml(source + os.sep + filename):
                    self.transformDigitalObjectToSID(filename, output, report)
    
    def transformDigitalObjectToSID(self, source, output, report=None):
        '''
        Transform a single digital object YAML record to Solr Input Document 
        format.
        '''
        if self._isDigitalObjectYaml(source):
            # read input file
            infile = open(source,'r')
            data = yaml.load(infile.read())
            infile.close()
            # create a new XML output file
            outfilename = "outfilename.xml"
            outpath = output + os.sep + outfilename
            outfile = open(outpath,'w')
            # transform
            len(data)
            # close
            outfile.close()
            self.logger.info("Wrote digital object YAML to SID " + outfilename)
            
    def transformEACCPFsToSid(self, sources, output, transform, report=None):
        '''
        Transform zero or more paths containing EAC-CPF documents to Solr Input
        Document format. 
        '''
        for source in sources:
            files = os.listdir(source)
            for filename in files:
                if self._isEACCPF(source + os.sep + filename):
                    self.transformEACCPFToSID(filename, output, transform, report)
    
    def transformEACCPFToSID(self, source, output, transform, report=None):
        '''
        Transform document to Solr Input Document format using the
        specified XSLT transform file.
        '''
        if self._isEACCPF(source):
            try:
                # read source data
                infile = open(source,'r')
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
                src_val, ref_val = self._getSourceAndReferrerValues(source)
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
                filename = self._getFileName(source)
                outfile = open(output + os.sep + filename, 'w')
                result.write(outfile, pretty_print=True, xml_declaration=True)
                outfile.close()
                self.logger.info("Transformed EAC-CPF to Solr Input Document " + filename)
            except Exception:
                self.logger.warning("Could not transform EAC-CPF " + filename, exc_info=True)

    def transformHtmlsToSid(self, sources, output, report):
        '''
        Transform HTML documents to Solr Input Document format.
        '''
        for source in sources:
            files = os.listdir(source)
            for filename in files:
                path = source + os.sep + filename
                html = HtmlPage(path)
                self.transformHtmlToSid(html, output, report)

    def transformHtmlToSid(self, html, output, report):
        '''
        Transform HTML to Solr Input Document format.
        '''
        data = html.getHtmlIndexContent()
        if 'abstract' in data:
            abstract = data['abstract']
        else:
            abstract = ""
        if 'title' in data:
            title = data['title']
        else:
            title = ""
        if 'uri' in data:
            uri = data['uri']
        else:
            uri = ""        
        outfile_path = output + os.sep + html.getRecordId() + ".xml"
        outfile = open(outfile_path,'w')
        outfile.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        outfile.write("<add>\n\t<doc>\n")
        outfile.write("\t\t<field name='abstract'>" + abstract + "</field>\n")
        outfile.write("\t\t<field name='title'>" + title + "</field>\n")
        outfile.write("\t\t<field name='referrer_uri'>" + uri + "</field>\n")
        outfile.write("\t</doc>\n</add>")
        outfile.close()
        self.logger.info("Transformed HTML to SID " + html.getUri())

    def validate(self, source, schema, report=None):
        '''
        Validate a collection of files against an XML schema.
        '''
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
