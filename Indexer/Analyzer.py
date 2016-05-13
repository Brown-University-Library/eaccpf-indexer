"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from .EacCpf import EacCpf
from io import StringIO
from datetime import datetime
from mako.template import Template
from lxml import etree

from . import Cfg
from . import Timer
from . import Utils
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

    def __init__(self, source, output, update=False):
        self.coordinates = {} # dictionary for geocoordinates
        self.hashIndex = {}
        self.logger = logging.getLogger()
        # set parameters
        self.output = output
        self.source = source
        self.update = update
        # load validation schema
        modpath = os.path.abspath(inspect.getfile(self.__class__))
        schema = os.path.dirname(modpath) + os.sep + 'transform' + os.sep + 'eaccpf.xsd'
        try:
            with open(schema, 'r') as f:
                schema_data = f.read()
                schema_root = etree.XML(schema_data)
                xmlschema = etree.XMLSchema(schema_root)
                self.parser = etree.XMLParser(schema=xmlschema)
                self.logger.info("Loaded EAC-CPF schema {0}".format(schema))
        except Exception:
            self.logger.error("Could not load schema file {0}".format(schema))

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

    def _isConformantToEacCpfSchema(self, Data):
        """
        Determine if the document is conformant to the EAC-CPF schema.
        """
        try:
            # etree.parse(StringIO(Data), self.parser)
            etree.parse(StringIO(Data))
            return True, []
        except:
            logging.error("Could not parse source file", exc_info=True)
            errors = []
            for entry in self.parser.error_log:
                error = str(entry.message)
                errors.append(error)
            return False, errors

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
            conformance, errors = self._isConformantToEacCpfSchema(doc.getData()) # @todo move to eaccpf
            analysis['conforms to schema'] = conformance
            # look for duplicate locations
            locations = doc.getLocations()
            duplicate = False
            for location in locations:
                if 'placeentry' in location:
                    place = location['placeentry']
                    if place in list(entity_locations.keys()):
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
            analysis['the section content counts'] = self._getSectionContentCounts(doc.getData()) # @todo move to eaccpf
            analysis['the total content count'] = self._getTotalContentCount(doc.getData()) # @todo move to eaccpf
            # @todo check paths for validity
            # @todo field level quality checks
            # write analysis file to the output path
            report['metadata'] = metadata
            report['analysis'] = analysis
            output_filename = Filename.replace('xml','yml')
            Utils.writeYaml(Output, output_filename, report)
            self.logger.info("Wrote analysis to: {0}".format(output_filename))
        except:
            # @todo write an output file for the failed input file, include the exception in the file
            self.logger.error("Could not complete analysis for: {0}".format(Filename), exc_info=Cfg.LOG_EXC_INFO)
        
    def analyzeFiles(self):
        """
        Analyze EAC-CPF files in the specified source paths. Write a YML file
        with analysis data to the output path.
        """
        records = []
        for filename in [f for f in os.listdir(self.source) if f.endswith(".xml")]:
            # if the file has not changed since the last run then skip it
            fileHash = Utils.getFileHash(self.source + os.sep + filename)
            if self.update:
                if filename in self.hashIndex and self.hashIndex[filename] == fileHash:
                    self.logger.info("No change since last update: {0}".format(filename))
                    continue
            # process the file
            records.append(filename)
            self.hashIndex[filename] = fileHash
            self.analyzeFile(self.source, filename, self.output)
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
        for filename in [f for f in files if f.endswith(".yml")]:
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
            self.logger.error("Could not write HTML report file", exc_info=Cfg.LOG_EXC_INFO)

    def run(self):
        """
        Execute analysis operations using specified parameters.
        """
        with Timer.Timer() as t:
            # make output folder
            if not os.path.exists(self.output):
                os.makedirs(self.output)
            if not self.update:
                Utils.cleanOutputFolder(self.output)
            # check state
            assert os.path.exists(self.source), self.logger.error("Source path does not exist: {0}".format(self.source))
            assert os.path.exists(self.output), self.logger.error("Output path does not exist: {0}".format(self.output))
            # create an index of file hashes, so that we can track what has changed
            if self.update:
                self.hashIndex = Utils.loadFileHashIndex(self.output)
            # analyze files
            records = self.analyzeFiles()
            # remove records from the index that were deleted in the source
            if self.update:
                self.logger.info("Clearing orphaned records from the file hash index")
                Utils.purgeIndex(records, self.hashIndex)
            # remove files from the output folder that are not in the index
            if self.update:
                self.logger.info("Clearing orphaned files from the output folder")
                Utils.purgeFolder(self.output, self.hashIndex)
            # build the HTML report
            self.buildHtmlReport(self.output, self.output, self.update)
            # write the updated file hash index
            Utils.writeFileHashIndex(self.hashIndex, self.output)
        # log execution time
        self.logger.info("Analyzer finished in {0}:{1}:{2}".format(t.hours, t.minutes, t.seconds))


def analyze(params, update=False):
    """
    Execute processing actions with the specified parameters.
    """
    source = params.get("analyze", "input")
    output = params.get("analyze", "output")
    analyzer = Analyzer(source, output, update)
    analyzer.run()