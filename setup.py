"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from setuptools import setup, find_packages

# @todo pull description, version number, etc from the README.md file
setup(name='Indexer',
      description="""A utility for indexing EAC-CPF and related content from a
      web site or file system, inferring data, post-processing and posting
      that data to an Apache Solr search index.""",
      author='(Davis Marques, Marco LaRosa) eScholarship Research Center, University of Melbourne',
      url='http://www.esrc.unimelb.edu.au',
      version='1.5.1',
      packages=find_packages(),
      install_requires=['lxml','pairtree','pyyaml','simplejson'],
)
