"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

__author__ = 'Davis Marques <dmarques@unimelb.edu.au>'

import logging
import networkx
import os
import shutil
import yaml

from EacCpf import EacCpf

class Grapher(object):
    """
    Builds a graph of EAC-CPF document, entity relationships. For each record,
    we store: record ID, title, abstract, existDates, metadata_url,
    presentation_url, function, localtype. type, cpfRelations,
    resourceRelations.

    http://www.findandconnect.gov.au/vic/eac/E000748.xml
    http://www.findandconnect.gov.au/vic/eac/E000244.xml
    http://www.findandconnect.gov.au/nsw/eac/NE00459.xml
    """

    def __init__(self):
        """
        Constructor
        """
        # logger
        self.logger = logging.getLogger('Grapher')
        pass

    def _makeCache(self, Path):
        """
        Create a cache folder at the specified path if none exists.
        If the path already exists, delete all files within it.
        """
        if os.path.exists(Path):
            shutil.rmtree(Path)
        os.makedirs(Path)
        self.logger.info("Cleared output folder at " + Path)

    def buildGraph(self, Source, Output):
        """
        Build graph representation from directory of YAML intermediate metadata
        files.
        """
        files = os.listdir(Source)
        for filename in files:
            if filename.endswith('.yml'):
                pass
        return None

    def process(self, Source, Output):
        """
        Process the source directory and write all graph related metadata to
        the YAML intermediate files in the specified output folder.
        """
        files = os.listdir(Source)
        for filename in files:
            if filename.endswith('.xml'):
                doc = EacCpf(Source + os.sep + filename)
                metadata = {}
                metadata['id'] = doc.getRecordId()
                metadata['title'] = doc.getTitle()
                metadata['abstract'] = doc.getAbstract()
                metadata['metadata_url'] = ''
                metadata['presentation_url'] = ''
                metadata['existdates'] = ''
                metadata['function'] = doc.getFunctions()
                metadata['entitytype'] = doc.getEntityType()
                metadata['localtype'] = doc.getLocalType()
                metadata['cpfrelations'] = doc.getCpfRelations()
                metadata['resourcerelations'] = doc.getResourceRelations()
                # write yaml file to output
                outfile_name = doc.getFileName().replace('xml','yml')
                outfile = open(Output + os.sep + outfile_name, 'w')
                yaml.dump(metadata,outfile)
                outfile.close()
                self.logger.info("Wrote graph data to " + outfile_name)

    def run(self, params):
        """
        Execute analysis operations using specified parameters.
        """
        # get parameters
        source = params.get("graph","input")
        output = params.get("graph","output")
        # make output folder
        self._makeCache(output)
        # check state
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        # execute actions
        self.process(source,output)
        self.buildGraph(output,output)

    def writeGraph(self,Graph):
        """
        Write graph to GEXML format file.
        """
        pass

