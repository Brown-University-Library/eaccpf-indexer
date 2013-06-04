"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

import inspect
import logging
import os
import shutil
import yaml
from BeautifulSoup import BeautifulSoup
from EacCpf import EacCpf
from StringIO import StringIO
from datetime import datetime
from mako.template import Template
from lxml import etree

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
        # load validation schema
        modpath = os.path.abspath(inspect.getfile(self.__class__))
        path = os.path.dirname(modpath)
        try:
            schema = path + os.sep + 'schema' + os.sep + 'eaccpf.xsd'
            infile = open(schema, 'r')
            schema_data = infile.read()
            schema_root = etree.XML(schema_data)
            xmlschema = etree.XMLSchema(schema_root)
            infile.close()
            self.logger.info("Loaded schema file " + schema)
        except Exception:
            self.logger.critical("Could not load schema file " + schema)
        # create validating parser
        self.parser = etree.XMLParser(schema=xmlschema)
        # dictionary for geocoordinates
        self.coordinates = {}

    def _getResourceRelations(self, Data):
        """
        Get a list of resource relations.
        """
        soup = BeautifulSoup(Data)
        relations = soup.find('relations')
        return relations.findChildren()
    
    def _getResourceRelationsCount(self, Data):
        """
        Get the number of resource relations in the document.
        """
        return len(self._getResourceRelations(Data))
    
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
            return True, ''
        except:
            errors = []
            for entry in self.parser.error_log:
                error = str(entry.message)
                errors.append(error)
            return False, errors

    def _isEacCpfFile(self, Path):
        """
        Determine if the document at the specified path is EAC-CPF.
        """
        if Path.endswith("xml"):
            infile = open(Path,'r')
            data = infile.read()
            infile.close()
            if "<eac-cpf" in data and "</eac-cpf>" in data:
                return True
        return False
    
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
        # read the input file
        infile = open(Source + os.sep + Filename,'r')
        data = infile.read()
        infile.close()
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
            conformance, errors = self._isConformantToEacCpfSchema(data)
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
            analysis['has duplicate place name'] = duplicate
            analysis['has location'] = doc.hasLocation()
            analysis['has maintenance record'] = doc.hasMaintenanceRecord()
            analysis['has record identifier'] = True if doc.getRecordId() != None else False
            analysis['has resource relations'] = doc.hasResourceRelations()
            analysis['the entity existence dates'] = doc.getExistDates()
            analysis['the entity type'] = doc.getEntityType()
            analysis['the entity local type'] = doc.getLocalType()
            analysis['the parsing errors'] = errors
            analysis['the resource relations count'] = self._getResourceRelationsCount(data)
            analysis['the section content counts'] = self._getSectionContentCounts(data)
            analysis['the total content count'] = self._getTotalContentCount(data)
            # @todo check paths for validity
            # @todo field level quality checks
            #  create an output file name
            output_filename = Filename.replace('xml','yml')
            # write analysis file to the output path
            report['metadata'] = metadata
            report['analysis'] = analysis
            outfile = open(Output + os.sep + output_filename, 'w')
            outfile.write(yaml.dump(report, indent=4))
            outfile.close()
            self.logger.info("Wrote analysis to " + output_filename)
        except:
            self.logger.warning("Could not complete analysis for " + Filename, exc_info=True)
        
    def analyzeFiles(self, Sources, Output):
        """
        Analyze EAC-CPF files in the specified source paths. Write a YML file
        with analysis data to the output path.
        """
        for source in Sources:
            files = os.listdir(source)
            for filename in files:
                if self._isEacCpfFile(source + os.sep + filename):
                    self.analyzeFile(source, filename, Output)

    def buildHtmlReport(self, Source, Output):
        """
        Build HTML report file
        """
        # copy the file from the template directory into the output directory 
        modpath = os.path.abspath(inspect.getfile(self.__class__))
        parentpath = os.path.dirname(modpath)
        assets = parentpath + os.sep + "template"
        shutil.copytree(assets + os.sep + 'assets',Output + os.sep + 'assets')
        templatefile = assets + os.sep + "index.mako"
        # build the report
        records = []
        files = os.listdir(Source)
        files.sort()
        # load analysis records
        for filename in files:
            try:
                path = Source + os.sep + filename
                if self._isAnalysisFile(path):
                    infile = open(path,'r')
                    data = infile.read()
                    record = yaml.load(data)
                    infile.close()
                    records.append(record)
            except:
                self.logger.warning("Could not process analysis file " + filename, exc_info=True)
        # load the template and update contents
        try:
            template = Template(filename=templatefile)
            reportdate = datetime.now().strftime("%B %d, %Y")
            data = template.render(date=reportdate,records=records,source=Source)
            # write the report
            outfile = open(Output + os.sep + 'index.html','w')
            outfile.write(data)
            outfile.close()
            self.logger.info("Wrote HTML report file")
        except:
            self.logger.warning("Could not write HTML report file", exc_info=True)

    def run(self, params):
        """
        Execute analysis operations using specified parameters.
        """
        # get parameters
        sources = params.get("analyze","inputs").split(',')
        output = params.get("analyze","output")
        # make output folder
        self._makeCache(output)
        # check state
        for source in sources:
            assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        # execute actions
        self.analyzeFiles(sources,output)
        self.buildHtmlReport(output,output)
        