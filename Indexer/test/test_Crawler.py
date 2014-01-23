"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from Indexer import Crawler

import unittest


class TestCrawler(unittest.TestCase):
    """
    Test cases for the Crawler module.
    """
    
    def setUp(self):
        """
        Setup the test environment.
        """
        pass
    
    def tearDown(self):
        """
        Tear down the test environment.
        """
        pass

    def test_init(self):
        """
        It should create an object instance.
        """
        pass

    def test_crawl(self):
        """
        It should retrieve files that exist. For each EAC-CPF file, it should
        add the metadata and presentation URLs as attributes to the eac-cpf
        node.
        """
        pass
    
if __name__ == '__main__':
    unittest.main()
