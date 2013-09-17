"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from Poster import Poster
from lxml import etree
import os
import unittest


class TestPoster(unittest.TestCase):
    """
    Executes unit tests against the Poster module.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.poster = Poster()
        self.url = "http://idx.internal:8080/solr/TEST"

    def tearDown(self):
        """
        Tear down the test environment.
        """
        pass
    
    def test_init(self):
        """
        It should create an instance of the Poster class.
        """
        self.assertNotEqual(self.poster,None)
        self.assertNotEqual(self.poster.logger,None)
    
    def test_commit(self):
        """
        It should send an HTTP message to the index to commit staged data.
        """
        try:
            code = self.poster.commit(self.url)
            self.assertLess(code, 400)
        except:
            self.fail("Failed to execute commit action on {0}".format(self.url))

    def test_flush(self):
        """
        It should send an HTTP message to the index to flush all live data.
        """
        try:
            code = self.poster.commit(self.url)
            self.assertLess(code, 400)
        except:
            self.fail("Failed to execute flush action on {0}".format(self.url))

    def test_optimize(self):
        """
        It should send a message to the index to optimize the live index,
        """
        try:
            code = self.poster.commit(self.url)
            self.assertLess(code, 400)
        except:
            self.fail("Failed to execute optimize action on {0}".format(self.url))

    def test_post(self):
        """
        It should execute an HTTP post of SID files from the source folder to
        the Solr index for staging.
        """
        pass

    def test_strip_empty_elements(self):
        """
        It should remove any elements that have no content.
        """
        path = os.path.dirname(__file__)
        case_0 = etree.parse(os.sep.join([path, 'test', 'poster', 'empty_tags_0.xml']))
        case_1 = etree.parse(os.sep.join([path, 'test', 'poster', 'empty_tags_1.xml']))
        case_2 = etree.parse(os.sep.join([path, 'test', 'poster', 'empty_tags_2.xml']))
        cases = [ case_0, case_1, case_2 ]
        for case in cases:
            self.poster.strip_empty_elements(case)
            for elem in case.iter('field'):
                if elem.text is None:
                    self.fail("Failed to remove empty element from {0}".format())


if __name__ == "__main__":
    unittest.main()
