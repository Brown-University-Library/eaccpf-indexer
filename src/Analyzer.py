'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from BeautifulSoup import BeautifulSoup
from StringIO import StringIO
from datetime import datetime
from lxml import etree
from mako.template import Template 

import inspect
import logging
import os
import shutil
import yaml

class Analyzer(object):
    '''
    EAC-CPF document analyzer. Performs a high level analysis of a document to
    produce an objective set of rudimentary metrics. These metrics may be used
    by an archivist or end user to make a quick, subjective assessment of the 
    state or quality of a single document in relation to a whole collection.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        # logger
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

    def _getEntityType(self, Data):
        '''
        Get the entity type.
        ex. <entityType>type</entityType>
        '''
        soup = BeautifulSoup(Data)
        tag = soup.find("entitytype")
        return str(tag.string)
        
    def _getEntityLocalType(self, Data):
        '''
        Get the entity local type.
        <localControl localType="typeOfEntity">
        <term>Organisation</term>
        </localControl>
        '''
        soup = BeautifulSoup(Data)
        tag = soup.find("localcontrol",{'localtype':'typeOfEntity'})
        if tag:
            thetype = tag.find("term")
            if thetype:
                return str(thetype.string)
            return tag.string
        return None

    def _getExistDates(self, Data):
        '''
        Get the list of existence dates for the entity.
        '''
        dates = []
        return dates

    def _getResourceRelations(self, Data):
        '''
        Get a list of resource relations.
        '''
        soup = BeautifulSoup(Data)
        relations = soup.find('relations')
        return relations.findChildren()
    
    def _getResourceRelationsCount(self, Data):
        '''
        Get the number of resource relations in the document.
        '''
        return len(self._getResourceRelations(Data))
    
    def _getSectionContentCount(self, Tag, Data):
        '''
        Get the number of characters between the open and closing section tags.
        '''
        starttag = "<" + Tag + ">"
        endtag = "</" + Tag + ">"
        start = Data.index(starttag)
        end = Data.index(endtag)
        return end - start - len(starttag)

    def _getSectionContentCounts(self, Data):
        '''
        Get a dictionary with content length counts for each section of the 
        document.
        '''
        counts = {}
        counts['control'] = self._getSectionContentCount("control", Data)
        counts['identity'] = self._getSectionContentCount("identity", Data)
        counts['description'] = self._getSectionContentCount("description", Data)
        counts['relations'] = self._getSectionContentCount("relations", Data)
        return counts

    def _getTotalContentCount(self, Data):
        '''
        Get the total number of characters comprising the EAC-CPF document.
        '''
        return len(Data)

    def _hasMaintenanceRecord(self, Data):
        '''
        Determine if the document has a maintenance record.
        '''
        return True

    def _hasRecordIdentifier(self, Data):
        '''
        Determine if the document has a record Id.
        '''
        soup = BeautifulSoup(Data)
        tag = soup.find("recordid")
        if tag:
            recordid = tag.string
            if recordid and len(recordid) > 0:
                return True
        return False

    def _hasResourceRelations(self, Data):
        '''
        Determine if the document has resource relations.
        '''
        count = self._getResourceRelationsCount(Data)
        if count is not None and count > 0:
            return True
        return False

    def _isConformantToEacCpfSchema(self, Data):
        '''
        Determine if the document is conformant to the EAC-CPF schema.
        '''
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
        '''
        Determine if the document at the specified path is EAC-CPF.
        '''
        if Path.endswith("xml"):
            infile = open(Path,'r')
            data = infile.read()
            infile.close()
            if "<eac-cpf" in data and "</eac-cpf>" in data:
                return True
        return False

    def _makeCache(self, Path):
        '''
        Create a folder at the specified path if none exists.
        If the path already exists, delete all files within it.
        '''
        if not os.path.exists(Path):
            os.makedirs(Path)
            self.logger.info("Created output folder at " + Path)
        else:
            files = os.listdir(Path)
            for filename in files:
                os.remove(Path + os.sep + filename)
            self.logger.info("Cleared output folder at " + Path)

    def analyzeFile(self, Source, Filename, Output):    
        '''
        Analyze EAC-CPF file for quality indicators and changes.
        '''
        # read the input file
        infile = open(Source + os.sep + Filename,'r')
        data = infile.read()
        infile.close()
        report = {}
        try:
            # the analysis
            analysis = {}
            analysis['the analysis date'] = datetime.now()
            conformance, errors = self._isConformantToEacCpfSchema(data)
            analysis['conforms to schema'] = conformance
            analysis['has maintenance record'] = self._hasMaintenanceRecord(data)
            analysis['has record identifier'] = self._hasRecordIdentifier(data)
            analysis['has resource relations'] = self._hasResourceRelations(data)
            analysis['the entity existence dates'] = self._getExistDates(data)
            analysis['the entity type'] = self._getEntityType(data)
            analysis['the entity local type'] = self._getEntityLocalType(data)
            analysis['the parsing errors'] = errors
            analysis['the resource relations count'] = self._getResourceRelationsCount(data)
            analysis['the section content counts'] = self._getSectionContentCounts(data)
            analysis['the total content count'] = self._getTotalContentCount(data)
            # @todo check paths for validity
            # field level quality checks
            # update the report file
            report['analysis'] = analysis
            outfile = open(Output + os.sep + Filename, 'w')
            outfile.write(yaml.dump(report, default_flow_style=False, indent=4))
            outfile.close()
            self.logger.info("Wrote analysis for " + Filename)
        except:
            self.logger.warning("Could not complete analysis for " + Filename, exc_info=True)
    
        
    def analyzeFiles(self, Source, Output):
        '''
        Analyze EAC-CPF files in the specified path. Write a report file to the
        report path.
        '''
        files = os.listdir(Source)
        for filename in files:
            if self._isEacCpfFile(Source + os.sep + filename):
                self.analyzeFile(Source, filename, Output)
                
    def buildHtmlReport(self, Source, Output):
        '''
        Build HTML report file 
        '''
        # copy the file from the template directory into the output directory 
        modpath = os.path.abspath(inspect.getfile(self.__class__))
        parentpath = os.path.dirname(modpath)
        assets = parentpath + os.sep + "template"
        for filename in os.listdir(assets):
            shutil.copyfile(assets + os.sep + filename, Output + os.sep + filename)
        templatefile = assets + os.sep + "index.mako"
        # build the report
        try:
            # load the template
            template = Template(filename=templatefile)
            data = template.render(Source=Source)
            # write the report
            outfile = open(Output + os.sep + 'index.html')
            outfile.write(data)
            outfile.close()
            self.logger.info("Wrote HTML report file")
        except:
            self.logger.warning("Could not write HTML report")
                
    def run(self, params):
        '''
        Execute analysis operations using specified parameters.
        '''
        # get parameters
        source = params.get("analyze","input")
        output = params.get("analyze","output")
        # make output folder
        self._makeCache(output)
        # check state
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Report path does not exist: " + output)
        # execute actions
        self.analyzeFiles(source,output)
        self.buildHtmlReport(source,output)
        