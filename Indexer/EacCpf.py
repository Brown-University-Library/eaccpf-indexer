"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from DigitalObject import DigitalObject
from lxml import etree

import Cfg
import Utils
import hashlib
import logging
import os
import urllib2

# namespaces
DOC_KEY = "doc"
DOC_NS = "urn:isbn:1-931666-33-4"

ESRC_KEY = "ns0"
ESRC_NS = "http://www.esrc.unimelb.edu.au"

XLINK = "http://www.w3.org/1999/xlink"
XSI = "http://www.w3.org/2001/XMLSchema-instance"


class EacCpf(object):
    """
    EAC-CPF documents provide metadata and references to external entities    
    that are the subject of indexing. This class wraps the EAC-CPF document 
    and provides convenience methods for extracting required metadata. The
    content of an EAC-CPF document is typically presented by a separate HTML
    document, referred to here as the presentation.
    """

    def __init__(self, Source, MetadataUrl=None, PresentationUrl=None):
        """
        Source is a file system path or URL to the EAC-CPF document file. The
        Source is used to load the content of the document. MetadataUrl is the
        public URL to the EAC-CPF document. PresentationUrl is the public URL
        to the HTML presentation.
        """
        self.log = logging.getLogger()
        self.metadata = MetadataUrl
        self.ns = { DOC_KEY: DOC_NS, ESRC_KEY: ESRC_NS }
        self.presentation = PresentationUrl
        self.source = Source
        data = Utils.load_from_source(Source)
        self.xml = etree.fromstring(data)
        # some documents may be missing the fully specified eac-cpf document
        # namespace attributes, which will result in failures during subsequent
        # operations. we'll check for the missing attribute here so that we can
        # make the problem and its resolution obvious in the log
        root = self.xml.xpath('//doc:eac-cpf', namespaces=self.ns)
        if len(root) == 0:
            self.log.error("Missing EAC-CPF namespace declaration in {0}".format(Source))
            raise Exception

    def getAbstract(self):
        """
        Get document abstract.
        """
        try:
            abstract = self.xml.xpath("//doc:eac-cpf/doc:cpfDescription/doc:description/doc:biogHist/doc:abstract", namespaces=self.ns)
            return abstract[0].text if abstract[0].text else None
        except:
            pass

    def getBiogHist(self):
        """
        Get the non-abstract portion of the biogHist entry.
        """
        try:
            val = self.xml.xpath("//doc:eac-cpf/doc:cpfDescription/doc:description/doc:biogHist/doc:p", namespaces=self.ns)
            if val:
                ps = []
                for p in val:
                    if p.text is not None:
                        ps.append(p.text)
                return ' '.join(ps)
        except:
            pass
        return None
 
    def getCpfRelations(self):
        """
        Get list of CPF relations.
        """
        rels = []
        try:
            cpfr = self.xml.xpath("//doc:eac-cpf/doc:cpfDescription/doc:relations/doc:cpfRelation", namespaces=self.ns)
            rels.extend(cpfr)
        except:
            pass
        return rels

    def getData(self):
        """
        Get the raw XML data.
        """
        return etree.tostring(self.xml, pretty_print=True)

    def getDigitalObjects(self, Thumbnail=False):
        """
        Get the list of digital objects referenced in the document. Transform
        the metadata contained in the HTML page to an intermediate YML digital
        object representation.
        """
        dobjects = []
        rels = self.xml.xpath("//doc:eac-cpf/doc:cpfDescription/doc:relations/doc:resourceRelation", namespaces=self.ns)
        for rel in rels:
            try:
                if rel.attrib['resourceRelationType'] == 'other':
                    relEntry = rel.xpath("./doc:relationEntry", namespaces=self.ns)
                    descNote = rel.xpath("./doc:descriptiveNote/doc:p", namespaces=self.ns)
                    if relEntry[0].attrib['localType'] == 'digitalObject':
                        # if the descriptiveNote does not contain the string "<p>Include in Gallery</p>",
                        # then it is not a thumbnail for this record
                        if Thumbnail and len(descNote) > 0 and not "Include in Gallery" in descNote[0].text:
                            continue
                        nz = {
                            "doc": "urn:isbn:1-931666-33-4",
                            "obj": "urn:isbn:1-931666-22-9",
                        }
                        # ISSUE #30 in some cases, the title string contains
                        # markup in it, which results in only a portion of the
                        # title string being returned. Here we concat the text
                        # content of all the child nodes together to create a
                        # single title string
                        title = ''
                        title_elements = rel.xpath("./doc:relationEntry", namespaces=self.ns)
                        for e in title_elements.pop().itertext():
                            title += e
                        # ISSUE #30: abstract may contain markup. concat all
                        # the child elements on to the abstract value.
                        abstract = ''
                        abstract_elements = rel.xpath("./doc:objectXMLWrap/obj:archref/obj:abstract", namespaces=nz)
                        for e in abstract_elements.pop().itertext():
                            abstract += e
                        alternate_title = self.getTitle()
                        localtype = self.getLocalType()
                        presentation = rel.attrib['{http://www.w3.org/1999/xlink}href']
                        unitdate = rel.xpath("./doc:objectXMLWrap/obj:archref/obj:unitdate", namespaces=nz)
                        # create the digital object
                        if unitdate and not hasattr(unitdate, 'lower'):
                            unitdate = unitdate[0].text
                            dobj = DigitalObject(self.source, self.metadata, presentation, title, abstract, localtype, UnitDate=unitdate, AlternateTitle=alternate_title)
                        else:
                            fromDate, toDate = self.getExistDates()
                            dobj = DigitalObject(self.source, self.metadata, presentation, title, abstract, localtype, FromDate=fromDate, ToDate=toDate, AlternateTitle=alternate_title)
                        dobjects.append(dobj)
            except:
                self.log.error("Could not retrieve digital object {0}".format(self.source), exc_info=Cfg.LOG_EXC_INFO)
        return dobjects

    def getEntityId(self):
        """
        Get the record entity Id. If a value can not be found None is returned.
        """
        try:
            val = self.xml.xpath("//doc:eac-cpf/doc:cpfDescription/doc:identity/doc:entityId", namespaces=self.ns)
            return val[0].text if val[0].text else None
        except:
            pass

    def getEntityType(self):
        """
        Get the entity type.
        """
        try:
            val = self.xml.xpath("//doc:eac-cpf/doc:cpfDescription/doc:identity/doc:entityType", namespaces=self.ns)
            return val[0].text if val[0].text else None
        except:
            pass

    def getExistDates(self):
        """
        Get entity exist dates. Returns 'from date', 'to date' tuple.
        """
        try:
            val = self.xml.xpath("//doc:eac-cpf/doc:cpfDescription/doc:description/doc:existDates", namespaces=self.ns)
            if val:
                fromDate = val[0].xpath("./doc:dateRange/doc:fromDate", namespaces=self.ns)
                toDate = val[0].xpath("./doc:dateRange/doc:toDate", namespaces=self.ns)
                if fromDate and len(fromDate) > 0 and 'standardDate' in fromDate[0].attrib:
                    fromDate = fromDate[0].attrib['standardDate']
                else:
                    fromDate = None
                if toDate and len(toDate) > 0 and 'standardDate' in toDate[0].attrib:
                    toDate = toDate[0].attrib['standardDate']
                else:
                    toDate = None
                # ensure dates are in ISO format
                if fromDate and not 'T00:00:00Z' in fromDate:
                    fromDate += "T00:00:00Z"
                if toDate and not 'T00:00:00Z' in toDate:
                    toDate += "T00:00:00Z"
                return fromDate, toDate
        except:
            pass
        return None, None

    def getFileName(self):
        """
        Get document file name.
        """
        return Utils.getFileName(self.source)

    def getFreeText(self):
        """
        Get content from free text fields.
        """
        freeText = ''
        names = self.getNameEntries()
        if names:
            freeText = ' '.join(names)
        abstract = self.getAbstract()
        if abstract:
            freeText += self.getAbstract() + ' '
        biog = self.getBiogHist()
        if biog:
            freeText += biog + ' '
        functions = self.getFunctions()
        if functions:
            freeText += ' '.join(functions)
        return freeText

    def getFunctions(self):
        """
        Get the functions.
        """
        functions = []
        try:
            val = self.xml.xpath("//doc:eac-cpf/doc:cpfDescription/doc:description/doc:functions/doc:function/doc:term", namespaces=self.ns)
            for func in val:
                if func.text is not None:
                    functions.append(func.text)
            return functions
        except:
            pass
        return functions

    def getHash(self):
        """
        Get a secure hash for the content in hexadecimal format.
        """
        h = hashlib.sha1()
        data = etree.tostring(self.xml)
        h.update(data)
        return h.hexdigest()

    def getLocalType(self):
        """
        Get the local type.
        """
        try:
            val = self.xml.xpath("//doc:eac-cpf/doc:control/doc:localControl/doc:term", namespaces=self.ns)
            return val[0].text if val[0].text else None
        except:
            pass

    def getLocations(self):
        """
        Get locations.
        """
        locations = []
        try:
            chronItems = self.xml.xpath("//doc:eac-cpf/doc:cpfDescription/doc:description/doc:biogHist/doc:chronList/doc:chronItem", namespaces=self.ns)
            for chronItem in chronItems:
                location = {}
                fromDate = chronItem.xpath("./doc:dateRange/doc:fromDate", namespaces=self.ns)
                toDate = chronItem.xpath("./doc:dateRange/doc:toDate", namespaces=self.ns)
                if fromDate and len(fromDate) > 0 and 'standardDate' in fromDate[0].attrib:
                    fromDate = fromDate[0].attrib['standardDate']
                    fromDate = Utils.fixIncorrectDateEncoding(fromDate)
                    location['fromDate'] = fromDate
                if toDate and len(toDate) and 'standardDate' in toDate[0].attrib:
                    toDate = toDate[0].attrib['standardDate']
                    toDate = Utils.fixIncorrectDateEncoding(toDate)
                    location['toDate'] = toDate
                placeEntry = chronItem.xpath("./doc:placeEntry", namespaces=self.ns)
                if placeEntry:
                    location['placeentry'] = placeEntry[0].text
                    if 'latitude' in placeEntry[0].attrib:
                        location['latitude'] = placeEntry[0].attrib['latitude']
                    if 'longitude' in placeEntry[0].attrib:
                        location['longitude'] = placeEntry[0].attrib['longitude']
                event = chronItem.xpath("./doc:event", namespaces=self.ns)
                if event:
                    location['event'] = event[0].text
                locations.append(location)
        except:
            pass
        return locations

    def getMetadataUrl(self):
        """
        Get the URL to the EAC-CPF document.
        """
        try:
            if 'http://' in self.source or 'https://' in self.source:
                return self.source
            elif self.metadata:
                return self.metadata
        except:
            pass
        return None

    def getNameEntries(self):
        """
        Get name entry.
        """
        names = []
        try:
            val = self.xml.xpath("//doc:eac-cpf/doc:cpfDescription/doc:identity/doc:nameEntry/doc:part", namespaces=self.ns)
            for part in val:
                for t in part.itertext():
                    names.append(t)
            return names
        except:
            pass
        return names

    def getPresentationUrl(self):
        """
        Get the URL to the HTML presentation of the EAC-CPF document.
        """
        if self.presentation:
            return self.presentation
        try:
            val = self.xml.xpath("//doc:eac-cpf/doc:cpfDescription/doc:identity/doc:entityId", namespaces=self.ns)
            return val[0].text if val[0].text else None
        except:
            pass

    def getRecordId(self):
        """
        Get the record identifier.
        """
        try:
            val = self.xml.xpath("//doc:eac-cpf/doc:control/doc:recordId", namespaces=self.ns)
            return val[0].text if val[0].text else None
        except:
            pass

    def getResourceRelations(self):
        """
        Get list of resource relations.
        """
        rels = []
        try:
            val = self.xml.xpath("//doc:eac-cpf/doc:cpfDescription/doc:relations/doc:resourceRelation", namespaces=self.ns)
            rels.extend(val)
        except:
            pass
        return rels

    def getTitle(self):
        """
        Get the record title.
        """
        names = self.getNameEntries()
        if names:
            return ' '.join(names)
        return None

    def getThumbnail(self):
        """
        Get the digital object that acts as a thumbnail image for this record.
        """
        try:
            obj = self.getDigitalObjects(Thumbnail=True)
            return obj[0]
        except:
            return None
    
    def hasDigitalObjects(self):
        """
        Determine if the EAC-CPF record has digital object references.
        """
        objects = self.getDigitalObjects()
        if objects and len(objects) > 0:
            return True
        return False

    def hasLocation(self):
        """
        Determine if the record has a location.
        """
        locations = self.getLocations()
        if len(locations) > 0:
            return True
        return False

    def hasMaintenanceRecord(self):
        """
        Determine if the record has a maintenance history section.
        """
        try:
            val = self.xml.xpath("//doc:eac-cpf/doc:control/doc:maintenanceHistory/doc:maintenanceEvent", namespaces=self.ns)
            if val and len(val) > 0:
                return True
        except:
            pass
        return False

    def hasResourceRelations(self):
        """
        Determine if the record has one or more resource relations.
        """
        cr = self.getCpfRelations()
        rr = self.getResourceRelations()
        if cr and rr and len(cr) > 0 and len(rr) > 0:
            return True
        return False

    def write(self, Path):
        """
        Write the EAC-CPF data to the specified path. Add the metadata,
        presentation source URLs as attributes to the eac-cpf node.
        """
        # add the metadata and presentation source URLs to the eac-cpf node
        root = self.xml.xpath('//doc:eac-cpf', namespaces=self.ns)
        metadata = '{' + ESRC_NS + '}metadata'
        presentation = '{' + ESRC_NS + '}presentation'
        source = '{' + ESRC_NS + '}source'
        root[0].set(metadata, self.metadata)
        root[0].set(presentation, self.presentation)
        root[0].set(source, self.source)
        # write the data to the specified path
        path = Path + os.sep + self.getFileName()
        with open(path, 'w') as outfile:
            data = etree.tostring(self.xml, pretty_print=True)
            outfile.write(data)
        self.log.info("Stored EAC-CPF document " + self.getFileName())
        return path
