"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from pip.req import parse_requirements
from setuptools import setup, find_packages

# read metadata
with open('README.md', 'r') as f:
    description = f.read()
version = '1.5.1'

# package requirements
install_reqs = parse_requirements('requirements.txt')
requirements = [str(ir.req) for ir in install_reqs]

setup(name='Indexer',
      description=description,
      author='Davis Marques <dmarques@unimelb.edu.au> eScholarship Research Center, University of Melbourne',
      url='http://www.esrc.unimelb.edu.au',
      version=version,
      packages=find_packages(),
      install_requires=requirements,
)
