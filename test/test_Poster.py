"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from Indexer import Poster
from lxml import etree

import inspect
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
        self.module = os.path.abspath(inspect.getfile(self.__class__))
        self.module_path = os.path.dirname(self.module)
        self.source = self.module_path + os.sep + "poster"
        self.url = "http://idx.internal:8080/solr/TEST"

    def tearDown(self):
        """
        Tear down the test environment.
        """
        pass
    
    def test__init__(self):
        """
        It should create an instance of the Poster class.
        """
        poster = Poster.Poster(self.source, self.url, ["flush"])
        self.assertNotEqual(None, poster)

    def test_commit(self):
        """
        It should send an HTTP message to the index to commit staged data.
        """
        try:
            poster = Poster.Poster(self.source, self.url, ['commit'])
            poster.run()
        except:
            self.fail("Failed to execute commit on {}".format(self.url))

    def test_flush(self):
        """
        It should send an HTTP message to the index to flush all live data.
        """
        try:
            poster = Poster.Poster(self.source, self.url, ['flush'])
            poster.run()
        except:
            self.fail("Failed to execute flush on {}".format(self.url))

    def test_optimize(self):
        """
        It should send a message to the index to optimize the live index,
        """
        try:
            poster = Poster.Poster(self.source, self.url, ['optimize'])
            poster.run()
        except:
            self.fail("Failed to execute optimize on {}".format(self.url))

    def test_post(self):
        """
        It should execute an HTTP post of SID files from the source folder to
        the Solr index for staging.
        """
        try:
            poster = Poster.Poster(self.source, self.url, ['post'])
            poster.run()
        except:
            self.fail("Failed to execute post on {}".format(self.url))

    def test_strip_empty_elements(self):
        """
        It should remove any elements that have no content.
        """
        poster = Poster.Poster(self.source, self.url, ['action'])
        path = os.path.dirname(__file__)
        case_0 = etree.parse(os.sep.join([path, 'poster', 'empty_tags_0.xml']))
        case_1 = etree.parse(os.sep.join([path, 'poster', 'empty_tags_1.xml']))
        case_2 = etree.parse(os.sep.join([path, 'poster', 'empty_tags_2.xml']))
        cases = [ case_0, case_1, case_2 ]
        for case in cases:
            poster.strip_empty_elements(case)
            for elem in case.iter('field'):
                if elem.text is None:
                    self.fail("Failed to remove empty element from {0}".format())


if __name__ == "__main__":
    unittest.main()
