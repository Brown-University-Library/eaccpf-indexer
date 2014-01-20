"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from HtmlPage import HtmlPage
from lxml import etree

import EacCpf
import inspect
import logging
import os
import shutil
import tempfile
import unittest


class TestDataExceptions(unittest.TestCase):
    """
    Unit tests for unique data cases that are causing failures in the current
    production indexer.
    """

    def setUp(self):
        """
        Setup the test environment.
        """
        self.module = os.path.abspath(inspect.getfile(self.__class__))
        self.module_path = os.path.dirname(self.module)
        self.log = logging.getLogger()
        self.temp = tempfile.mkdtemp()
        self.test_site = os.sep.join([self.module_path, "test", "test_site"])
        self.test_eac = self.test_site + os.sep + 'eac' + os.sep

    def tearDown(self):
        """
        Tear down the test environment.
        """
        if os.path.exists(self.temp):
            shutil.rmtree(self.temp)

    def test_getDigitalObjects_exceptions(self):
        """
        For the set of special cases, get the list of digital objects.
        These cases are currently failing with the production indexer.
        """
        test_data = os.sep.join([self.module_path, "test", "exceptions"])
        cases = [
            (test_data + os.sep + "E000111.xml", 1),
            (test_data + os.sep + "QE00003.xml", 3) # has 3 DOs, but only
        ]
        for case in cases:
            source, expected = case
            doc = EacCpf.EacCpf(source, "http://www.findandconnect.gov.au/", "http://www.findandconnect.gov.au/")
            self.assertNotEqual(None, doc)
            result = doc.getDigitalObjects()
            self.assertEqual(expected, len(result))


if __name__ == "__main__":
    unittest.main()