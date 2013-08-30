"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from EacCpf import EacCpf
from StringIO import StringIO
from datetime import datetime
from mako.template import Template
from lxml import etree
import Utils
import inspect
import logging
import os
import shutil


class Analyzer(object):
    """
    EAC-CPF document analyzer. Performs a high level analysis of a document to
    produce an objective set of rudimentary metrics. These metrics may be used
    by an archivist or end user to make a quick, subjective assessment of the
    state or quality of a single document in relation to a whole collection.
    """

    def __init__(self):
        """
        Constructor
        """
        self.logger = logging.getLogger('Analyzer')
        self.coordinates = {} # dictionary for geocoordinates
        # load validation schema
        modpath = os.path.abspath(inspect.getfile(self.__class__))
        path = os.path.dirname(modpath)
        try:
            schema = path + os.sep + 'transform' + os.sep + 'eaccpf.xsd'
            infile = open(schema, 'r')
            schema_data = infile.read()
            schema_root = etree.XML(schema_data)
            xmlschema = etree.XMLSchema(schema_root)
            infile.close()
            self.logger.info("Loaded schema file " + schema)
            self.parser = etree.XMLParser(schema=xmlschema)
        except Exception:
            self.logger.error("Could not load schema file " + schema)

    def _getResourceRelations(self, Data):
        """
        Get a list of resource relations.
        """
        tree = etree.parse(Data)
        relations = tree.findall('//relations')
        return relations.findChildren()

    def _getSectionContentCount(self, Tag, Data):
        """
        Get the number of characters between the open and closing section tags.
        """
        starttag = "<" + Tag + ">"
        endtag = "</" + Tag + ">"
        start = Data.index(starttag)
        end = Data.index(endtag)
        return end - start - len(starttag)

    def _getSectionContentCounts(self, Data):
        """
        Get a dictionary with content length counts for each section of the
        document.
        """
        counts = {}
        counts['control'] = self._getSectionContentCount("control", Data)
        counts['identity'] = self._getSectionContentCount("identity", Data)
        counts['description'] = self._getSectionContentCount("description", Data)
        counts['relations'] = self._getSectionContentCount("relations", Data)
        return counts
    
    def _getTotalContentCount(self, Data):
        """
        Get the total number of characters comprising the EAC-CPF document.
        """
        return len(Data)

    def _isAnalysisFile(self,Path):
        """
        Determine if the file at the specified path is an analysis file.
        """
        if Path.endswith("yml"):
            return True
        return False

    def _isConformantToEacCpfSchema(self, Data):
        """
        Determine if the document is conformant to the EAC-CPF schema.
        """
        try:
            etree.parse(StringIO(Data), self.parser)
            return True, []
        except:
            errors = []
            for entry in self.parser.error_log:
                error = str(entry.message)
                errors.append(error)
            return False, errors

    def _makeCache(self, Path):
        """
        Create a folder at the specified path if none exists.
        If the path already exists, delete all files within it.
        """
        if not os.path.exists(Path):
            os.makedirs(Path)
            self.logger.info("Created output folder at " + Path)
        else:
            shutil.rmtree(Path)
            os.makedirs(Path)
            self.logger.info("Cleared output folder at " + Path)

    def analyzeFile(self, Source, Filename, Output):    
        """
        Analyze EAC-CPF file for quality indicators and changes. Write a YAML
        file with analysis data to the output path.
        """
        try:
            report = {}
            entity_locations = {}
            doc = EacCpf(Source + os.sep + Filename, None)
            # get some basic metadata for the file
            metadata = {}
            metadata['id'] = doc.getRecordId()
            metadata['entityid'] = doc.getEntityId()
            metadata['entitytype'] = doc.getEntityType()
            metadata['localtype'] = doc.getLocalType()
            metadata['title'] = doc.getTitle()
            # analyze the file
            analysis = {}
            analysis['the analysis date'] = datetime.now()
            conformance, errors = self._isConformantToEacCpfSchema(doc.data) # @todo move to eaccpf
            analysis['conforms to schema'] = conformance
            # look for duplicate locations
            locations = doc.getLocations()
            duplicate = False
            for location in locations:
                if 'placeentry' in location:
                    place = location['placeentry']
                    if place in entity_locations.keys():
                        duplicate = True
                        errors.append("Location '" + place + "' duplicates record '" + entity_locations[place] + "'")
                    else:
                        entity_locations[place] = metadata['id']
            analysis['has abstract'] = True if doc.getAbstract() != '' else False
            analysis['has duplicate place name'] = duplicate
            analysis['has location'] = doc.hasLocation()
            analysis['has maintenance record'] = doc.hasMaintenanceRecord()
            analysis['has record identifier'] = True if doc.getRecordId() != None else False
            analysis['has resource relations'] = doc.hasResourceRelations()
            analysis['the entity existence dates'] = doc.getExistDates()
            analysis['the entity type'] = doc.getEntityType()
            analysis['the entity local type'] = doc.getLocalType()
            analysis['the parsing errors'] = errors
            rrels = doc.getResourceRelations()
            analysis['the resource relations count'] = len(rrels) if rrels != None else 0
            analysis['the section content counts'] = self._getSectionContentCounts(doc.data) # @todo move to eaccpf
            analysis['the total content count'] = self._getTotalContentCount(doc.data) # @todo move to eaccpf
            # @todo check paths for validity
            # @todo field level quality checks
            # write analysis file to the output path
            report['metadata'] = metadata
            report['analysis'] = analysis
            output_filename = Filename.replace('xml','yml')
            Utils.writeYaml(Output, output_filename, report)
            self.logger.info("Wrote analysis to " + output_filename)
        except:
            self.logger.error("Could not complete analysis for " + Filename, exc_info=True)
        
    def analyzeFiles(self, Source, Output, HashIndex, Update):
        """
        Analyze EAC-CPF files in the specified source paths. Write a YML file
        with analysis data to the output path.
        """
        records = []
        files = os.listdir(Source)
        for filename in files:
            if filename.endswith(".xml"):
                # if the file has not changed since the last run then skip it
                fileHash = Utils.getFileHash(Source + os.sep + filename)
                if Update:
                    if filename in HashIndex and HashIndex[filename] == fileHash:
                        self.logger.info("No change since last update " + filename)
                        continue
                # process the file
                records.append(filename)
                HashIndex[filename] = fileHash
                self.analyzeFile(Source, filename, Output)
        return records

    def buildHtmlReport(self, Source, Output, Update):
        """
        Build HTML report file
        """
        modPath = os.path.abspath(inspect.getfile(self.__class__))
        parentPath = os.path.dirname(modPath)
        assets_input = parentPath + os.sep + "template"
        assets_output = Output + os.sep + 'assets'
        templateFile = assets_input + os.sep + "index.mako"
        # copy HTML assets to the output path
        try:
            if os.path.exists(assets_output):
                shutil.rmtree(assets_output) # copytree won't work if there is an existing target
            shutil.copytree(assets_input + os.sep + 'assets', assets_output)
        except:
            pass
        # build the report
        records = []
        files = os.listdir(Source)
        files.sort()
        # load analysis data 
        for filename in files:
            if filename.endswith(".yml"):
                record = Utils.readYaml(Source, filename)
                records.append(record)
        # load the template and update contents
        try:
            template = Template(filename=templateFile)
            reportDate = datetime.now().strftime("%B %d, %Y")
            data = template.render(date=reportDate,records=records,source=Source)
            # write the report
            Utils.write(Output, 'index.html', data)
            self.logger.info("Wrote HTML report file")
        except:
            self.logger.error("Could not write HTML report file", exc_info=True)

    def run(self, Params, Update=False):
        """
        Execute analysis operations using specified parameters.
        """
        # get parameters
        source = Params.get("analyze", "input")
        output = Params.get("analyze", "output")
        # make output folder
        if not os.path.exists(output):
            os.makedirs(output)
        if not Update:
            Utils.cleanOutputFolder(output)
        # check state
        assert os.path.exists(source), self.logger.error("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.error("Output path does not exist: " + output)
        # create an index of file hashes, so that we can track what has changed
        hashIndex = {}
        if Update:
            hashIndex = Utils.loadFileHashIndex(output)
        # analyze files
        records = self.analyzeFiles(source, output, hashIndex, Update)
        # remove records from the index that were deleted in the source
        if Update:
            self.logger.info("Clearing orphaned records from the file hash index")
            Utils.purgeIndex(records, hashIndex)
        # remove files from the output folder that are not in the index
        if Update:
            self.logger.info("Clearing orphaned files from the output folder")
            Utils.purgeFolder(output, hashIndex)
        # build the HTML report
        self.buildHtmlReport(output, output, Update)
        # write the updated file hash index
        Utils.writeFileHashIndex(hashIndex, output)
