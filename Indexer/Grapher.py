"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from EacCpf import EacCpf
import Utils
import logging
import networkx as nx
import os
import yaml

LOG_EXC_INFO = False


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
        self.logger = logging.getLogger()

    def graph(self, Source, Output):
        """
        Build graph representation from directory of YAML intermediate metadata
        files.
        """
        g = nx.Graph()
        files = os.listdir(Source)
        for filename in files:
            if filename.endswith('.yml'):
                infile = open(Source + os.sep + filename,'r')
                data = infile.read()
                data = yaml.load(data)
                infile.close()
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

    def run(self, Params, Update=False, StackTrace=False):
        """
        Execute analysis operations using specified parameters.
        """
        # get parameters
        source = Params.get("graph","input")
        output = Params.get("graph","output")
        try:
            gexf = Params.get("graph","graphmodel")
        except:
            gexf = None
        # make output folder
        Utils.cleanOutputFolder(output)
        # check state
        assert os.path.exists(source), self.logger.error("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.error("Output path does not exist: " + output)
        # execute actions
        self.summarize(source, output)
        self.graph(output, gexf)

    def summarize(self, Source, Output):
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
                outfile = open(Output + os.sep + outfile_name, 'w')
                yaml.dump(metadata,outfile)
                outfile.close()
                self.logger.info("Wrote graph data to " + outfile_name)
