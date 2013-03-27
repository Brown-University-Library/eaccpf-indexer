'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from datetime import datetime
from lxml import etree
import logging
import os
import yaml

class Analyzer(object):
    '''
    EAC-CPF document analyzer. Performs a high level analysis of a document to
    produce an objective set of rudimentary metrics. These metrics may be used
    by an archivist or end user to make a quick, subjective assessment of the 
    state or quality of a single document in relation to a whole collection.
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        # logger
        self.logger = logging.getLogger('Analyzer')
        # load validation schema
        path = os.path.dirname(Analyzer.__file__)
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
        '''
        return 'type'

    def _getEntityLocalType(self, Data):
        '''
        Get the entity local type.
        '''
        return 'localtype'

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
        pass
    
    def _getResourceRelationsCount(self, Data):
        '''
        Get the number of resource relations in the document.
        '''
        return len(self._getResourceRelations(Data))
    
    def _getSectionContentCounts(self, Data):
        '''
        Get a dictionary with content length counts for each section of the 
        document.
        '''
        counts = {}
        return counts

    def _getTotalContentCount(self, Data):
        '''
        Get the total number of characters comprising the EAC-CPF document.
        '''
        return 0

    def _hasMaintenanceRecord(self, Data):
        '''
        Determine if the document has a maintenance record.
        '''
        return True

    def _hasRecordIdentifier(self, Data):
        '''
        Determine if the document has a record Id.
        '''
        return True

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
            etree.fromstring(Data, self.parser)
            return True
        except Exception:
            return False

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

    def analyzeFile(self, Path, Filename, Report):    
        '''
        Analyze EAC-CPF file for quality indicators and changes.
        @todo Report should be the output path, not a file. The output file 
        name can be inferred from the input filename.
        '''
        # read the input file
        infile = open(Path,'r')
        data = infile.read()
        infile.close()
        # read the existing report file
        reportfile = open(Report,'r+')
        report = yaml.load(reportfile.read())
        try:
            # the analysis
            analysis = {}
            # basic document quality indicators
            analysis['the analysis date'] = datetime.now()
            analysis['conforms to schema'] = self._isConformantToEacCpfSchema(data)  
            analysis['has maintenance record'] = self._hasMaintenanceRecord(data)
            analysis['has record identifier'] = self._hasRecordIdentifier(data)
            analysis['has resource relations'] = self._hasResourceRelations(data)
            analysis['the entity existence dates'] = self._getExistDates(data)
            analysis['the entity type'] = self._getEntityType(data)
            analysis['the entity local type'] = self._getEntityLocalType(data)
            analysis['the resource relations count'] = self._getResourceRelationsCount(data)
            analysis['the section content counts'] = self._getSectionContentCounts(data)
            analysis['the total content count'] = self._getTotalContentCount(data)
            # field level quality checks
            # update the report file
            report['analysis'] = analysis
            reportfile.write(yaml.dump(report, default_flow_style=False, indent=4))
        except:
            self.logger.warning("Could not complete analysis for " + Filename)
        finally:
            reportfile.close()
            self.logger.info("Wrote analysis for " + Filename)
    
    def analyzeFiles(self, Path, Output):
        '''
        Analyze EAC-CPF files in the specified path.
        '''
        files = os.listdir(Path)
        for filename in files:
            if self._isEacCpfFile(Path + os.sep + filename):
                self.analyzeFile(Path, filename, Output + os.sep + filename)
                
    def run(self, params):
        '''
        Execute analysis operations using specified parameters.
        '''
        # get parameters
        source = params.get("analyze","source")
        report = params.get("analyze","report")
        # check state
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # execute actions
        self.analyzeFiles(source,report)
        