"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from lxml import etree
import HtmlPage
import Utils
import logging
import os
import yaml

LOG_EXC_INFO = False


class Transformer(object):
    """
    Transform and merge source data to Solr Input Document format.
    """

    def __init__(self):
        self.log = logging.getLogger('Transformer')

    def _getIdFromFilename(self,Filename):
        """
        Get the record ID from the filename.
        """
        recordId, _ = os.path.splitext(Filename)
        return recordId

    def mergeDigitalObjectIntoSID(self, Source, Output):
        """
        Merge the digital object record into the Solr Input Document. Do not
        overwrite existing id, presentation_url and metadata_url fields.
        """
        filename = ''
        try:
            # read the digital object metadata file
            infile = open(Source, 'r')
            data = infile.read()
            dobj = yaml.load(data)
            infile.close()
            filename = Utils.getFileName(Source).replace('.yml', '.xml')
            # if there is an existing SID file, then read it
            if os.path.exists(Output + os.sep + filename):
                parser = etree.XMLParser(remove_blank_text=True)
                xml = etree.parse(Output + os.sep + filename, parser)
                root = xml.getroot()
                doc = root.getchildren()[0]
                # add fields that are not already present in the SID file
                for fieldname in dobj.keys():
                    if fieldname.startswith('dobj'):
                        # if the field already exists then update it, otherwise add it
                        node = doc.xpath("//field[@name='{0}']".format(fieldname))
                        if node and len(node) > 0:
                            node[0].text = dobj[fieldname]
                        else:
                            dobjfield = etree.Element("field", name=fieldname)
                            dobjfield.text = dobj[fieldname]
                            doc.append(dobjfield)
                # write the updated file
                outfile = open(Output + os.sep + filename,'w')
                xml.write(outfile, pretty_print=True, xml_declaration=True)
                outfile.close()
                self.log.info("Merged digital object into {0}".format(filename))
        except:
            self.log.error("Could not complete merge processing for {0}".format(filename), exc_info=LOG_EXC_INFO)
    
    def mergeDigitalObjectsIntoSID(self, Sources, Output):
        """
        Merge digital object records into Solr Input Documents.
        """
        for source in Sources:
            files = os.listdir(source)
            for filename in files:
                if Utils.isDigitalObjectYaml(source + os.sep + filename):
                    path = source + os.sep + filename
                    self.mergeDigitalObjectIntoSID(path, Output)
                    
    def mergeInferredRecordIntoSID(self, Source, Output):
        """
        Merge inferred data into Solr Input Document. Write merged data to 
        output.
        """
        filename = ''
        try:
            # read input (inferred) data file
            infile = open(Source, 'r')
            data = infile.read()
            inferred = yaml.load(data)
            infile.close()
            filename = Utils.getFileName(Output)
            # if there is an existing SID file, then read it into memory, 
            # otherwise create an XML tree to 
            if not os.path.exists(Output):
                root = etree.Element("add")
                xml = etree.ElementTree(root)
                doc = etree.Element("doc")
                root.append(doc)
                # add required records
                recordId = etree.Element("field", name="id")
                recordId.text = self._getIdFromFilename(filename)
                doc.append(recordId)
            else:
                # read output (Solr Input Document) data file
                parser = etree.XMLParser(remove_blank_text=True)
                xml = etree.parse(Output, parser)
                root = xml.getroot()
                doc = root.getchildren()[0]
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
                        city.text = location['city']
                        doc.append(city)
                        # state
                        region = etree.Element('field', name='region')
                        region.text = location['region']
                        doc.append(region)
                        # region
                        country = etree.Element('field', name='country')
                        country.text = location['country']
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
                outfile = open(Output,'w')
                xml.write(outfile, pretty_print=True, xml_declaration=True)
                outfile.close()
                self.log.info("Merged inferred data into {0}".format(filename))
        except Exception:
            self.log.error("Could not complete merge processing for {0}".format(filename), exc_info=LOG_EXC_INFO)
    
    def mergeInferredRecordsIntoSID(self, Sources, Output):
        """
        Transform zero or more paths with inferred object records to Solr Input 
        Document format.
        """
        for source in Sources:
            files = os.listdir(source)
            for filename in files:
                if Utils.isInferredYaml(source + os.sep + filename):
                    outputFileName = self._getIdFromFilename(filename) + ".xml"
                    self.mergeInferredRecordIntoSID(source + os.sep + filename, Output + os.sep + outputFileName)
    
    def run(self, Params):
        """
        Execute transformations on source documents as specified. Write results 
        to the output path.
        """
        # get parameters
        actions = Params.get("transform", "actions").split(',')
        output = Params.get("transform", "output")
        sources = Params.get("transform", "inputs").split(",")
        # create output folder
        if not os.path.exists(output):
            os.makedirs(output)
        Utils.cleanOutputFolder(output)
        # check state
        assert os.path.exists(output), self.log.error("Output path does not exist: {0}".format(output))
        for source in sources:
            assert os.path.exists(source), self.log.error("Source path does not exist: {0}".format(source))
        # execute actions in order
        if "digitalobjects-to-sid" in actions:
            self.transformDigitalObjectsToSID(sources, output)
        if "eaccpf-to-sid" in actions:
            if Params.has_option("transform", "xslt"):
                xslt = Params.get("transform", "xslt")
            else:
                modpath = os.path.abspath(__file__)
                xslt = os.path.dirname(modpath) + os.sep + "transform" + os.sep + 'esrc-eaccpf-to-solr.xsl'
            transform = Utils.loadTransform(xslt)
            self.transformEacCpfsToSID(sources, output, transform)
        if "html-to-sid" in actions:
            self.transformHtmlsToSid(sources, output)
        if 'merge-digitalobjects' in actions:
            self.mergeDigitalObjectsIntoSID(sources, output)
        if "merge-inferred" in actions:
            self.mergeInferredRecordsIntoSID(sources, output)
        if "set-fields" in actions:
            fields = Params.get("transform", "set-fields").split(",")
            if not ('' in fields):
                self.setFieldValue(output, fields)
        if 'boost' in actions:
            boosts = Params.get("transform", "boost").split(',')
            self.setBoosts(output, boosts)
        if "validate" in actions:
            pass
            # schema = Params.get("transform","schema")

    def setBoosts(self, Source, Boosts):
        """
        Boost the specified field for all Solr Input Documents.
        """
        files = os.listdir(Source)
        for filename in files:
            path = Source + os.sep + filename
            if Utils.isSolrInputDocument(path):
                try:
                    # parse the document
                    xml = etree.parse(path)
                    for boost in Boosts:
                        fieldname, boostval = boost.split(':')
                        fields = xml.findall('//field[@name="' + fieldname + '"]')
                        for field in fields:
                            field.attrib['boost'] = boostval
                    # save the document
                    outfile = open(path, 'w')
                    data = etree.tostring(xml, pretty_print=True, xml_declaration=True)
                    outfile.write(data)
                    outfile.close()
                    msg = "Set boosts: {0}".format(filename)
                    self.log.info(msg)
                except:
                    msg = "Could not set boosts: {0}".format(filename)
                    self.log.error(msg, exc_info=LOG_EXC_INFO)

    def setFieldValue(self, Source, Values):
        """
        Set the specified field value for all Solr Input Documents.
        """
        files = os.listdir(Source)
        parser = etree.XMLParser(remove_blank_text=True)
        for filename in files:
            if Utils.isSolrInputDocument(Source + os.sep + filename):
                try:
                    # load the document
                    xml = etree.parse(Source + os.sep + filename, parser)
                    root = xml.getroot()
                    doc = root.getchildren()[0]
                    # set the field values
                    for fieldvalue in Values:
                        fieldname, value = fieldvalue.split(":")
                        fields = doc.findall('field[@name="' + fieldname + '"]')
                        # if the field exists, change its value
                        if len(fields) > 0:
                            for field in fields:
                                field.text = value
                        else:
                            newfield = etree.Element("field", name=fieldname)
                            newfield.text = value
                            doc.append(newfield)
                    # save the updated document
                    outfile = open(Source + os.sep + filename,'w')
                    data = etree.tostring(xml, pretty_print=True, xml_declaration=True)
                    outfile.write(data)
                    outfile.close()
                    self.log.info("Set fields in {0}".format(filename))
                except:
                    self.log.error("Could not set field in {0}".format(filename))

    def transformDigitalObjectToSID(self, Source, Output, Transform=None):
        """
        Transform a single digital object YAML record to Solr Input Document
        format.
        """
        # read digital object data
        infile = open(Source, 'r')
        data = yaml.load(infile.read())
        infile.close()
        # create SID document
        root = etree.Element("add")
        doc = etree.SubElement(root, "doc")
        for key in data:
            f = etree.SubElement(doc, "field")
            f.attrib['name'] = key
            if data[key] and len(data[key]) > 0:
                f.text = data[key]
        # write XML
        filename = Utils.getFileName(Source)
        filename = Utils.getFilenameWithAlternateExtension(filename, "xml")
        outfile = open(Output + os.sep + filename,'w')
        xml = etree.tostring(root, pretty_print=True, xml_declaration=True)
        outfile.write(xml)
        outfile.close()
        self.log.info("Transformed dobject to SID: {0}".format(filename))

    def transformDigitalObjectsToSID(self, Sources, Output, Transform=None):
        """
        Transform zero or more paths with digital object YAML records to Solr 
        Input Document format.
        """
        for source in Sources:
            files = os.listdir(source)
            for filename in files:
                path = source + os.sep + filename
                if Utils.isDigitalObjectYaml(path):
                    try:
                        self.transformDigitalObjectToSID(path, Output)
                    except:
                        msg = "Could not transform DObject to SID: {0}".format(filename)
                        self.log.error(msg, exc_info=LOG_EXC_INFO)

    def transformEacCpfToSID(self, Source, Output, Transform):
        """
        Transform EAC-CPF document to Solr Input Document format using the
        specified XSLT transform file.
        """
        xml = etree.parse(Source)
        result = Transform(xml)
        # write the output file
        filename = Utils.getFileName(Source)
        outfile = open(Output + os.sep + filename, 'w')
        data = etree.tostring(result, pretty_print=True, xml_declaration=True)
        outfile.write(data)
        outfile.close()
        self.log.info("Transformed EAC-CPF to SID: {0}".format(filename))

    def transformEacCpfsToSID(self, Sources, Output, Transform):
        """
        Transform zero or more paths containing EAC-CPF documents to Solr Input
        Document format.
        """
        for source in Sources:
            files = os.listdir(source)
            for filename in files:
                if filename.endswith(".xml"):
                    try:
                        self.transformEacCpfToSID(source + os.sep + filename, Output, Transform)
                    except Exception:
                        msg = "Could not transform EAC-CPF to SID: {0}".format(filename)
                        self.log.error(msg, exc_info=LOG_EXC_INFO)

    def transformHtmlToSid(self, Html, Output):
        """
        Transform HTML document to Solr Input Document.
        """
        data = Html.getHtmlIndexContent()
        filename = Html.getFilename()
        record_id = Html.getRecordId()
        # create XML document
        root = etree.Element("add")
        doc = etree.SubElement(root, "doc")
        for key in data:
            f = etree.SubElement(doc, "field")
            f.attrib['name'] = key
            f.text = data[key]
        # write XML
        outfile = open(Output + os.sep + record_id + ".xml", 'w')
        xml = etree.tostring(root, pretty_print=True)
        outfile.write(xml)
        outfile.close()
        msg = "Transformed HTML to SID: {0}".format(filename)
        self.log.info(msg)

    def transformHtmlsToSid(self, Sources, Output):
        """
        Transform HTML documents to Solr Input Document format.
        """
        for source in Sources:
            files = os.listdir(source)
            for filename in files:
                if filename.endswith('htm') or filename.endswith('html'):
                    path = source + os.sep + filename
                    html = HtmlPage.HtmlPage(path)
                    try:
                        self.transformHtmlToSid(html, Output)
                    except:
                        msg = "Could not transform HTML to SID: {0}".format(filename)
                        self.log.error(msg)

