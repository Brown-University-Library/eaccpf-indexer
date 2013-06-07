"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from BeautifulSoup import BeautifulSoup
from DigitalObject import DigitalObject
from lxml import etree
import Utils
import hashlib
import logging
import os
import urllib2


class EacCpf(object):
    """
    EAC-CPF documents provide metadata and references to external entities    
    that are the subject of indexing. This class wraps the EAC-CPF document 
    and provides convenience methods for extracting required metadata. The
    content of an EAC-CPF document is typically presented by a separate HTML
    document, referred to here as the presentation.
    """

    def __init__(self, Source, MetadataUrl=None, PresentationUrl=None, Data=None):
        """
        Source is a file system path or URL to the EAC-CPF document file. The
        Source is used to load the content of the document. MetadataUrl is the
        public URL to the EAC-CPF document. PresentationUrl is the public URL
        to the HTML presentation.
        """
        self.logger = logging.getLogger('EacCpf')
        self.source = Source
        self.metadata = MetadataUrl
        self.presentation = PresentationUrl
        if Data:
            self.data = Data
        else:
            self.data = self._load(Source)
        self.soup = BeautifulSoup(self.data)
        self.xml = etree.fromstring(self.data)

    def _getTagString(self, Tag):
        """
        Get tag string value.
        :param Tag:
        """
        if Tag and Tag.string:
            return str(Tag.string)
        return None

    def _isEACCPF(self):
        """
        Determines if the file at the specified path is EAC-CPF. 
        """
        if "<eac-cpf" in self.data and "</eac-cpf>" in self.data:
            return True
        return False

    def _load(self, Source):
        """
        Load the document content.
        """
        try:
            if 'http://' in Source or 'https://' in Source:
                response = urllib2.urlopen(Source)
                return response.read()
            else:
                infile = open(Source)
                data = infile.read()
                infile.close()
                return data
        except:
            return None

    def getAbstract(self):
        """
        Get document abstract.
        """
        try:
            return str(self.soup.find('description').find('bioghist').find('abstract').string)
        except:
            return ''
        
    def getCpfRelations(self):
        """
        Get list of CPF relations.
        """
        try:
            relations = []
            cpfr = self.soup.findAll('cpfrelation')
            for rel in cpfr:
                relation = {}
                for attr, val in rel.attrs:
                    if attr == 'cpfrelationtype':
                        relation['type'] = str(rel['cpfrelationtype'])
                    elif attr == 'xlink:type':
                        relation['xlink:type'] = str(rel['xlink:type'])
                    elif attr == 'xlink:href':
                        relation['xlink:href'] = str(rel['xlink:href'])
                relationEntry = rel.find('relationentry')
                if relationEntry:
                    relation['relationentry'] = str(relationEntry.text)
                    relation['relationentry_localtype'] = str(relationEntry['localtype'])
                note = rel.find('descriptivenote')
                if note:
                    relation['descriptivenote'] = str(rel.find('descriptivenote').text)
                relations.append(relation)
            return relations
        except:
            return []
        
    def getDigitalObject(self, Record, Thumbnail=False):
        """
        Transform the metadata contained in the HTML page to an intermediate 
        YML digital object representation.
        """
        try:
            # if the resource contains a relationEntry with localType attribute = 'digitalObject'
            entry = Record.find('relationentry', {'localtype':'digitalObject'})
            if entry:
                if Thumbnail:
                    note = Record.find('descriptivenote')
                    # if the entry does not have a descriptiveNote or the descriptiveNote
                    # does not contain the string "<p>Include in Gallery</p>", then it is
                    # not a thumbnail for this record
                    if not note or not "Include in Gallery" in note.text:
                        return None
                presentation = Record['xlink:href'].encode("utf-8")
                title = str(entry.string)
                abstract = self._getTagString(Record.find('abstract'))
                entitytype = self.getEntityType()
                localtype = self.getLocalType()
                # @todo location
                unitdate = self._getTagString(Record.find('unitdate'))
                dobj = DigitalObject(self.source, self.metadata, presentation, title, abstract, entitytype, localtype, unitdate)
                return dobj
            # no digital object found
            return None
        except:
            return None

    def getDigitalObjects(self, Thumbnail=False):
        """
        Get the list of digital objects referenced in the document.
        """
        dobjects = []
        resources = self.soup.findAll('resourcerelation')
        for resource in resources:
            dobject = self.getDigitalObject(resource, Thumbnail)
            if dobject:
                dobjects.append(dobject)
        return dobjects
    
    def getEntityId(self):
        """
        Get the record entity Id
        """
        try:
            val = self.soup.find('identity').find('entityid').string
            return str(val)
        except:
            return None
    
    def getEntityType(self):
        """
        Get the entity type.
        """
        try:
            val = self.soup.find('entitytype').string
            return str(val)
        except:
            return None

    def getExistDates(self):
        """
        Get entity exist dates. Returns 'from date', 'to date' list.
        """
        try:
            existDates = self.soup.find('existdates')
            fromDate = existDates.find('daterange').find('fromdate')
            toDate = existDates.find('daterange').find('todate')
            if fromDate and 'standarddate' in dict(fromDate.attrs):
                fromDate = fromDate['standarddate']
            if toDate and 'standarddate' in dict(toDate.attrs):
                toDate = toDate['standarddate']
            return fromDate, toDate
        except:
            return None

    def getFileName(self):
        """
        Get document file name.
        """
        if "/" in self.source:
            parts = self.source.split("/")
            return parts[-1]
        return self.source
    
    def getFreeText(self):
        """
        Get content from free text fields.
        """
        freeText = ''
        # /eac-cpf/identity/nameEntry/part
        try:
            parts = self.soup.find('nameentry').findAll('part')
            for p in parts:
                freeText += Utils.cleanText(p.getString())
        except:
            pass
        # /eac-cpf/description/biogHist/abstract
        try:
            abstract = self.soup.find('bioghist').find('abstract')
            freeText += Utils.cleanText(abstract.getText())
        except:
            pass
        # /eac-cpf/description/biogHist/p
        try:
            ps = self.soup.find('bioghist').findAll('p')
            for p in ps:
                freeText += Utils.cleanText(p.getString())
        except:
            pass
        # /eac-cpf/description/function/descNote/p
        try:
            functions = self.soup.find('function').findAll('p')
            for f in functions:
                freeText += Utils.cleanText(f.getString())
        except:
            pass
        # return
        return freeText

    def getFunctions(self):
        """
        Get the functions.
        """
        functions = self.soup.findAll('function')
        result = []
        for function in functions:
            try:
                term = function.find("term")
                result.append(str(term.string))
            except:
                pass
        return result
    
    def getHash(self):
        """
        Get a secure hash for the content in hexadecimal format.
        """
        h = hashlib.sha1()
        h.update(self.data)
        return h.hexdigest()

    def getLocalType(self):
        """
        Get the local type.
        """
        try:
            ltype = self.soup.find('localcontrol').find('term')
            return ltype.string.encode("utf-8")
        except:
            return None

    def getLocations(self):
        """
        Get locations.
        """
        locations = []
        try:
            chronItems = self.soup.findAll('chronitem')
            for chronItem in chronItems:
                location = {}
                dateRange = chronItem.find('daterange')
                placeEntry = chronItem.find('placeentry')
                event = chronItem.find('event')
                if dateRange:
                    fromDate = dateRange.find('fromdate')
                    toDate = dateRange.find('todate')
                    if fromDate and 'standarddate' in dict(fromDate.attrs):
                        fromDate = fromDate['standarddate']
                        fromDate = Utils.fixIncorrectDateEncoding(fromDate)
                    if toDate and 'standarddate' in dict(toDate.attrs):
                        toDate = toDate['standarddate']
                        toDate = Utils.fixIncorrectDateEncoding(toDate)
                    location['fromDate'] = str(fromDate)
                    location['toDate'] = str(toDate)
                if placeEntry:
                    location['placeentry'] = str(placeEntry.text)
                if event:
                    location['event'] = str(event.text)
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
            else:
                return None
        except:
            return None

    def getPresentationUrl(self):
        """
        Get the URL to the HTML presentation of the EAC-CPF document.
        """
        try:
            if self.presentation:
                return self.presentation
            else:
                entityid = self.soup.find('entityid')
                url = entityid.text
                return str(url)
        except:
            return None

    def getRecordId(self):
        """
        Get the record identifier.
        @todo the identifier should come from the data rather than the file name
        """
        try:
            record = self.soup.find("recordid")
            if record:
                return record.text
            return None
        except:
            return None

    def getResourceRelations(self):
        """
        Get list of resource relations.
        """
        try:
            relations = []
            rels = self.soup.findAll('resourcerelation')
            for rel in rels:
                relation = {}
                for attr, val in rel.attrs:
                    if attr == 'resourcerelationtype':
                        relation['type'] = str(rel['resourcerelationtype'])
                    elif attr == 'xlink:type':
                        relation['xlink:type'] = str(rel['xlink:type'])
                    elif attr == 'xlink:href':
                        relation['xlink:href'] = str(rel['xlink:href'])
                relationEntry = rel.find('relationentry')
                if relationEntry:
                    relation['relationentry'] = str(relationEntry.text)
                    relation['relationentry_localtype'] = str(relationEntry['localtype'])
                note = rel.find('descriptivenote')
                if note:
                    relation['descriptivenote'] = str(rel.find('descriptivenote').text)
                relations.append(relation)
            return relations
        except:
            return []
    
    def getTitle(self):
        """
        Get the record title.
        """
        try:
            identity = self.soup.find('identity')
            nameentry = identity.find('nameentry')
            nameparts = nameentry.findAll('part')
            if nameparts:
                title = ''
                for part in nameparts:
                    title = title + part.string + ' '
                return str(title)
        except:
            return None
    
    def getThumbnail(self):
        """
        Get the digital object that acts as a thumbnail image for this record.
        """
        try:
            objs = self.getDigitalObjects(Thumbnail=True)
            return objs[0]
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
            events = self.soup.find('control').find('maintenancehistory').findAll('maintenanceevent')
            if len(events) > 0:
                return True
            return False
        except:
            return False

    def hasResourceRelations(self):
        """
        Determine if the record has one or more resource relations.
        """
        try:
            rels = self.soup.find('relations')
            if rels:
                cpf = rels.findAll('cpfrelation')
                rrel = rels.findAll('resourcerelation')
                if len(cpf) + len(rrel) > 0:
                    return True
            return False
        except:
            return False

    def write(self, Path):
        """
        Write the EAC-CPF data to the specified path.
        """
        path = Path + os.sep + self.getFileName()
        outfile = open(path, 'w')
        outfile.write(self.data)
        outfile.write('\n<!-- @source=%(source)s @metadata=%(metadata)s @presentation=%(presentation)s -->' %
                      {"source":self.source, "metadata":self.metadata, "presentation":self.presentation})
        outfile.close()
        self.logger.info("Stored EAC-CPF document " + self.getFileName())
