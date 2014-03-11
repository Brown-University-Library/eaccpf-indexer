"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from EacCpf import EacCpf
from HtmlPage import HtmlPage
from matplotlib import pylab

import Cfg
import Utils
import logging
import matplotlib.pyplot as plt
import networkx as nx
import re
import os
import tempfile

GRAPH_FILE = "graph.gml"

class Grapher(object):
    """
    Builds a graph of EAC-CPF document, entity relationships. For each record,
    we store: record ID, title, abstract, existDates, metadata_url,
    presentation_url, function, localtype. type, cpfRelations,
    resourceRelations.

    We can merge inferred data into the graph as well.
    """

    def __init__(self, source, output, inferred, base, actions, exclude):
        self.log = logging.getLogger()
        self.actions = actions
        self.base = base if base else None
        self.exclude = exclude if exclude else []
        self.graph = nx.Graph()
        self.inferred = inferred
        self.output = output
        self.source = source
        # compile exclude patterns
        self.exclude_match = []
        for pattern in self.exclude:
            p = re.compile(pattern)
            self.exclude_match.append(p)

    def _is_excluded(self, path):
        """
        Return True if the file or directory should be excluded based on
        whether its name matches a pattern specified as part of the exclude
        list. Return False otherwise.
        """
        for pattern in self.exclude_match:
            if pattern.match(path):
                return True
        return False

    def graph_entities(self):
        """
        Build a graph representation of a collection.
        When we search the graph in the presentation interface, we are going to
        be displaying HTML documents.
        """
        # walk the source directory
        for path, sub_dirs, files in os.walk(self.source):
            # remove excluded subdirectories from the traversal list
            for sub_dir in [d for d in sub_dirs if self._is_excluded(d)]:
                sub_dirs.remove(sub_dir)
            # construct an assumed public url for the path
            base_url = self.base + path.replace(self.source, '')
            base_url += '/' if not base_url.endswith('/') else ''
            # scan the current path
            self.log.debug("Scanning {0} ({1})".format(path, base_url))
            for filename in [f for f in files if f.endswith(".htm") or f.endswith(".html")]:
                self.log.debug("Reading {0}".format(filename))
                try:
                    html = HtmlPage(path, filename, base_url)
                    if html.hasEacCpfAlternate():
                        html_id = html.getRecordId()
                        html_url = html.getUrl()
                        html_title = html.getTitle()
                        self.graph.add_node(html_url, id=html_id, label=html_title, type="html")
                        metadata_url = html.getEacCpfUrl()
                        presentation_url = html.getUrl()
                        eac_path = self.source + metadata_url.replace(self.base, '')
                        if not os.path.exists(eac_path):
                            self.log.warning("EAC-CPF resource not available at {0}".format(eac_path))
                        else:
                            eac = EacCpf(eac_path, metadata_url, presentation_url)
                            eac_id = eac.getRecordId()
                            eac_title = eac.getTitle()
                            self.graph.add_node(metadata_url, id=eac_id, label=eac_title, type="eaccpf")
                            self.graph.add_edge(metadata_url, html_url, label="presentation")
                            self.log.debug("Added node {0}".format(metadata_url))
                            if 'entity-type'in self.actions:
                                eac_type = eac.getEntityType()
                                self.graph.add_node(eac_type, type="entity-type")
                                self.graph.add_edge(metadata_url, eac_type)
                            if 'local-type' in self.actions:
                                eac_local_type = eac.getLocalType()
                                self.graph.add_node(eac_local_type, type="local-type")
                                self.graph.add_edge(metadata_url, eac_local_type)
                            if 'function' in self.actions:
                                functions = eac.getFunctions()
                                for f in functions:
                                    self.graph.add_node(f, type="function")
                                    self.graph.add_edge(metadata_url, f)
                            if 'relation' in self.actions:
                                for rel in eac.getCpfRelationLinks():
                                    rel_url, title = rel
                                    self.graph.add_node(rel_url, label=title, type="relation")
                                    self.graph.add_edge(metadata_url, rel_url)
                                for rel in eac.getResourceRelationLinks():
                                    rel_url, title = rel
                                    self.graph.add_node(rel_url, label=title, type="relation")
                                    self.graph.add_edge(metadata_url, rel_url)
                except:
                    self.log.error("Could not complete processing for {0}".format(filename), exc_info=Cfg.LOG_EXC_INFO)

    def graph_inferred(self):
        """
        """
        pass

    def run(self):
        """
        Execute analysis operations using specified parameters.
        """
        # make output folder
        Utils.cleanOutputFolder(self.output)
        # check state
        assert os.path.exists(self.source), self.log.error("Source path does not exist: " + self.source)
        assert os.path.exists(self.output), self.log.error("Output path does not exist: " + self.output)
        # execute actions
        self.graph_entities()
        # generate a PDF of the graph
        self.save_graph_as_pdf()
        # write graph file
        self.save_graph_as_gexf()

    def save_graph_as_gexf(self):
        tmp = tempfile.mktemp(prefix="graph-", suffix=".gexf")
        nx.write_gexf(self.graph, tmp)

    def save_graph_as_pdf(self):
        tmp = tempfile.mktemp(prefix="graph-", suffix=".pdf")
        #initialze Figure
        plt.figure(num=None, figsize=(20, 20), dpi=80)
        plt.axis('off')
        fig = plt.figure(1)
        pos = nx.spring_layout(self.graph)
        nx.draw_networkx_nodes(self.graph, pos)
        nx.draw_networkx_edges(self.graph, pos)
        nx.draw_networkx_labels(self.graph, pos)

        cut = 1.00
        xmax = cut * max(xx for xx, yy in pos.values())
        ymax = cut * max(yy for xx, yy in pos.values())
        plt.xlim(0, xmax)
        plt.ylim(0, ymax)

        plt.savefig(tmp, bbox_inches="tight")
        pylab.close()
        del fig

def graph(params, update):
    """
    Execute processing actions with the specified parameters.
    """
    base = params.get("graph","base")
    source = params.get("graph","input")
    output = params.get("graph","output")
    inferred = params.get("graph", "inferred") if params.has_option("graph", "inferred") else ''
    actions = params.get("graph", "actions").split(',') if params.has_option("graph", "actions") else []
    exclude = params.get("graph", "exclude").split(',') if params.has_option("graph", "exclude") else []
    grapher = Grapher(source, output, inferred, base, actions, exclude)
    grapher.run()
