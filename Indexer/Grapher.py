"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from EacCpf import EacCpf

import Cfg
import Utils

import glob
import logging
import networkx as nx
import os
import yaml



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

    def __init__(self, source, output, gexf):
        self.logger = logging.getLogger()
        self.source = source
        self.output = output
        self.gexf = gexf

    def graph(self, Source, Output):
        """
        Build graph representation from directory of YAML intermediate metadata
        files.
        """
        g = nx.Graph()
        for filename in glob.glob(Source + os.sep + "*.yml"):
            with open(Source + os.sep + filename,'r') as infile:
                data = infile.read()
                data = yaml.load(data)
            # create the node
            g.add_node(data['presentation_url'], label=data['id'], data=data)
            # create the relationships
            for rel in data['cpfrelations']:
                pass
            for rel in data['resourcerelations']:
                # if the relation is to another document, then just create an edge
                if 'xlink:href' in rel:
                    g.add_edge(data['presentation_url'], rel['xlink:href'])
                # else, create a node to represent the entity and then link to it
                else:
                    rel['title'] = rel['relationentry']
                    g.add_node(rel['relationentry'], data=rel)
                    g.add_edge(data['presentation_url'], rel['title'])
        # draw the graph
        nx.draw_spring(g)
        # write the graph file
        # nx.write_gexf(g, Output)

    def jsongraph(self, Source):
        """
        Build a JSON graph representation directly from the input EAC-CPF data
        source.
        """
        pass

    def run(self):
        """
        Execute analysis operations using specified parameters.
        """
        # make output folder
        Utils.cleanOutputFolder(self.output)
        # check state
        assert os.path.exists(self.source), self.logger.error("Source path does not exist: " + self.source)
        assert os.path.exists(self.output), self.logger.error("Output path does not exist: " + self.output)
        # execute actions
        self.summarize(self.source, self.output)
        self.graph(self.output, self.gexf)

    def summarize(self, Source, Output):
        """
        Process the source directory and write all graph related metadata to
        the YAML intermediate files in the specified output folder.
        """
        for filename in glob.glob(Source + os.sep + "*.xml"):
            doc = EacCpf(Source + os.sep + filename)
            metadata = {}
            metadata['id'] = doc.getRecordId()
            metadata['title'] = doc.getTitle()
            metadata['abstract'] = doc.getAbstract()
            metadata['metadata_url'] = doc.getMetadataUrl()
            metadata['presentation_url'] = doc.getPresentationUrl()
            metadata['existdates'] = ''
            metadata['function'] = doc.getFunctions()
            metadata['entitytype'] = doc.getEntityType()
            metadata['localtype'] = doc.getLocalType()
            metadata['cpfrelations'] = doc.getCpfRelations()
            metadata['resourcerelations'] = doc.getResourceRelations()
            # write yaml file to output
            outfile_name = doc.getFileName().replace('xml','yml')
            with open(Output + os.sep + outfile_name, 'w') as outfile:
                yaml.dump(metadata,outfile)
            self.logger.info("Wrote graph data to {0}".format(outfile_name))


def graph(params, update):
    """
    Execute processing actions with the specified parameters.
    """
    # get parameters
    source = params.get("graph","input")
    output = params.get("graph","output")
    try:
        gexf = params.get("graph","graphmodel")
    except:
        gexf = None
    grapher = Grapher(source, output, gexf)
    grapher.run()