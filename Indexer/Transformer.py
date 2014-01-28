"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from lxml import etree

import Cfg
import HtmlPage
import Utils
import logging
import os
import yaml


class Transformer(object):
    """
    Transform and merge source data to Solr Input Document format. Transform
    does not use the --update flag because the operation is purely local and
    should take an insignificant amount of time to complete.
    """

    def __init__(self, actions, boosts, fields, output, sources, transform=None):
        self.log = logging.getLogger()
        # set parameters
        self.actions = actions
        self.boosts = boosts
        self.fields = fields
        self.output = output
        self.sources = sources
        if transform:
            self.xslt = transform
        else:
            # use default transform
            self.modpath = os.path.abspath(__file__)
            self.xslt = os.path.dirname(self.modpath) + os.sep + "transform" + os.sep + 'esrc-eaccpf-to-solr.xsl'

    def mergeDigitalObjectIntoSID(self, path, filename, output_path):
        """
        Merge the digital object record into the Solr Input Document. Do not
        overwrite existing id, presentation_url and metadata_url fields.
        """
        try:
            # read the digital object metadata file
            with open(path + os.sep + filename, 'r') as f:
                data = f.read()
                dobj = yaml.load(data)
            # if there is an existing SID file, then read it
            if os.path.exists(output_path + os.sep + filename):
                parser = etree.XMLParser(remove_blank_text=True)
                xml = etree.parse(output_path + os.sep + filename, parser)
                root = xml.getroot()
                doc = root.getchildren()[0]
            else:
                # @todo else create an empty SID document object; we won't likely hit this case
                return
            # add fields that are not already present in the SID file
            for field_name in dobj.keys():
                if field_name.startswith('dobj'):
                    # if the field already exists then update it, otherwise add it
                    node = doc.xpath("//field[@name='{0}']".format(field_name))
                    if node and len(node) > 0:
                        node[0].text = dobj[field_name]
                    else:
                        dobjfield = etree.Element("field", name=field_name)
                        dobjfield.text = dobj[field_name]
                        doc.append(dobjfield)
            # write the updated file
            output_filename = Utils.getFilenameWithAlternateExtension(filename, 'xml')
            with open(output_path + os.sep + output_filename,'w') as outfile:
                xml.write(outfile, pretty_print=True, xml_declaration=True)
            self.log.info("Merged digital object into {0}".format(output_filename))
        except:
            self.log.error("Could not complete merge processing for {0}".format(filename), exc_info=Cfg.LOG_EXC_INFO)
    
    def mergeDigitalObjectsIntoSID(self, Sources, Output):
        """
        Merge digital object records into Solr Input Documents.
        """
        for source in [s for s in Sources if os.path.exists(s)]:
            for filename in [f for f in os.listdir(source) if f.endswith(".yml")]:
                self.mergeDigitalObjectIntoSID(source, filename, Output)
                    
    def mergeInferredRecordIntoSID(self, Source, Output):
        """
        Merge inferred data into Solr Input Document. Write merged data to 
        output.
        """
        filename = ''
        try:
            # read input (inferred) data file
            with open(Source, 'r') as infile:
                data = infile.read()
                inferred = yaml.load(data)
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
                recordId.text = Utils.getRecordIdFromFilename(filename)
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
            self.log.error("Could not complete merge processing for {0}".format(filename), exc_info=Cfg.LOG_EXC_INFO)
    
    def mergeInferredRecordsIntoSID(self, Sources, Output):
        """
        Transform zero or more paths with inferred object records to Solr Input 
        Document format.
        """
        for source in [s for s in Sources if os.path.exists(s)]:
            for filename in [f for f in os.listdir(source) if f.endswith(".yml")]:
                output_filename = Utils.getFilenameWithAlternateExtension(filename, "xml")
                self.mergeInferredRecordIntoSID(source + os.sep + filename, Output + os.sep + output_filename)
    
    def run(self):
        """
        Execute transformations on source documents as specified. Write results 
        to the output path.
        """
        # create output folder
        if not os.path.exists(self.output):
            os.makedirs(self.output)
        Utils.cleanOutputFolder(self.output)
        assert os.path.exists(self.output), self.log.error("Output path does not exist: {0}".format(self.output))
        # execute processing actions
        if "digitalobjects-to-sid" in self.actions:
            self.transformDigitalObjectsToSID(self.sources, self.output)
        if "eaccpf-to-sid" in self.actions:
            transform = Utils.loadTransform(self.xslt)
            self.transformEacCpfsToSID(self.sources, self.output, transform)
        if "html-to-sid" in self.actions:
            self.transformHtmlsToSid(self.sources, self.output)
        if 'merge-digitalobjects' in self.actions:
            self.mergeDigitalObjectsIntoSID(self.sources, self.output)
        if "merge-inferred" in self.actions:
            self.mergeInferredRecordsIntoSID(self.sources, self.output)
        if "set-fields" in self.actions:
            if not ('' in self.fields):
                self.setFieldValue(self.output, self.fields)
        if 'boost' in self.actions:
            self.setBoosts(self.output, self.boosts)
        if "validate" in self.actions:
            pass

    def setBoosts(self, Source, Boosts):
        """
        Boost the specified field for all Solr Input Documents.
        """
        for filename in [f for f in os.listdir(Source) if f.endswith(".xml")]:
            try:
                # update the document
                xml = etree.parse(Source + os.sep + filename)
                for fieldname, boostval in [boost.split(':') for boost in Boosts]:
                    fields = xml.findall('//field[@name="' + fieldname + '"]')
                    for field in fields:
                        field.attrib['boost'] = boostval
                # save the document
                with open(Source + os.sep + filename, 'w') as outfile:
                    data = etree.tostring(xml, pretty_print=True, xml_declaration=True)
                    outfile.write(data)
                self.log.info("Set boosts: {0}".format(filename))
            except:
                self.log.error("Could not set boosts: {0}".format(filename), exc_info=Cfg.LOG_EXC_INFO)

    def setFieldValue(self, Source, Values):
        """
        Set the specified field value for all Solr Input Documents.
        """
        parser = etree.XMLParser(remove_blank_text=True)
        for filename in [f for f in os.listdir(Source) if f.endswith(".xml")]:
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
                with open(Source + os.sep + filename,'w') as outfile:
                    data = etree.tostring(xml, pretty_print=True, xml_declaration=True)
                    outfile.write(data)
                self.log.info("Set fields in {0}".format(filename))
            except:
                self.log.error("Could not set field in {0}".format(filename), exc_info=Cfg.LOG_EXC_INFO)

    def transformDigitalObjectToSID(self, path, filename, Output, Transform=None):
        """
        Transform a single digital object YAML record to Solr Input Document
        format.
        """
        # read digital object data
        with open(path + os.sep + filename, 'r') as f:
            data = yaml.load(f.read())
        # create SID document
        root = etree.Element("add")
        doc = etree.SubElement(root, "doc")
        for key in data:
            f = etree.SubElement(doc, "field")
            f.attrib['name'] = key
            if data[key] and len(data[key]) > 0:
                f.text = data[key]
        # write XML
        filename = Utils.getFilenameWithAlternateExtension(filename, "xml")
        with open(Output + os.sep + filename,'w') as outfile:
            xml = etree.tostring(root, pretty_print=True, xml_declaration=True)
            outfile.write(xml)
        self.log.info("Transformed dobject to SID: {0}".format(filename))

    def transformDigitalObjectsToSID(self, Sources, Output, Transform=None):
        """
        Transform zero or more paths with digital object YAML records to Solr 
        Input Document format.
        """
        for source in [s for s in Sources if os.path.exists(s)]:
            for filename in [f for f in os.listdir(source) if f.endswith(".yml")]:
                try:
                    self.transformDigitalObjectToSID(source, filename, Output)
                except:
                    msg = "Could not transform digital object to SID: {0}".format(filename)
                    self.log.error(msg, exc_info=Cfg.LOG_EXC_INFO)

    def transformEacCpfToSID(self, path, filename, Output, Transform):
        """
        Transform EAC-CPF document to Solr Input Document format using the
        specified XSLT transform file.
        """
        xml = etree.parse(path + os.sep + filename)
        result = Transform(xml)
        data = etree.tostring(result, pretty_print=True, xml_declaration=True)
        # write the output file
        with open(Output + os.sep + filename, 'w') as outfile:
            outfile.write(data)
        self.log.info("Transformed EAC-CPF to SID: {0}".format(filename))

    def transformEacCpfsToSID(self, Sources, Output, Transform):
        """
        Transform zero or more paths containing EAC-CPF documents to Solr Input
        Document format.
        """
        for source in [s for s in Sources if os.path.exists(s)]:
            for filename in [f for f in os.listdir(source) if f.endswith(".xml")]:
                try:
                    self.transformEacCpfToSID(source, filename, Output, Transform)
                except Exception:
                    msg = "Could not transform EAC-CPF to SID: {0}".format(filename)
                    self.log.error(msg, exc_info=Cfg.LOG_EXC_INFO)

    def transformHtmlToSid(self, Html, Output):
        """
        Transform HTML document to Solr Input Document.
        """
        # create SID document
        data = Html.getHtmlIndexContent()
        root = etree.Element("add")
        doc = etree.SubElement(root, "doc")
        for key in data:
            f = etree.SubElement(doc, "field")
            f.attrib['name'] = key
            f.text = data[key]
        # write SID document
        filename = data['id'] + ".xml"
        with open(Output + os.sep + filename, 'w') as f:
            xml = etree.tostring(root, pretty_print=True)
            f.write(xml)
        self.log.info("Transformed HTML to SID: {0}".format(filename))

    def transformHtmlsToSid(self, Sources, Output):
        """
        Transform HTML documents to Solr Input Document format.
        """
        for source in [s for s in Sources if os.path.exists(s)]:
            for filename in [f for f in os.listdir(source) if f.endswith('.htm') or f.endswith('.html')]:
                html = HtmlPage.HtmlPage(source, filename=filename)
                try:
                    self.transformHtmlToSid(html, Output)
                except:
                    msg = "Could not transform HTML to SID: {0}".format(filename)
                    self.log.error(msg, exc_info=Cfg.LOG_EXC_INFO)


def transform(params):
    """
    Execute transform operation with the specified parameters.
    """
    actions = params.get("transform", "actions").split(',')
    boosts = params.get("transform", "boost").split(',')
    fields = params.get("transform", "set-fields").split(",")
    output = params.get("transform", "output")
    sources = params.get("transform", "inputs").split(",")
    if params.has_option("transform", "xslt"):
        xslt = params.get("transform", "xslt")
    else:
        xslt=None
    transformer = Transformer(actions, boosts, fields, output, sources, transform=xslt)
    transformer.run()
