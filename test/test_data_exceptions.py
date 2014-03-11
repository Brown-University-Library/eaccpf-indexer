"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from lxml import etree

from Indexer import EacCpf
from Indexer import HtmlPage

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
        self.test_site = os.sep.join([self.module_path, "test_site"])
        self.test_eac = self.test_site + os.sep + 'eac' + os.sep

    def tearDown(self):
        """
        Tear down the test environment.
        """
        shutil.rmtree(self.temp, ignore_errors=True)

    def test_eaccpf_getDigitalObjects_exceptions(self):
        """
        For the set of special cases, get the list of digital objects.
        These cases are currently failing with the production indexer.
        """
        test_data = os.sep.join([self.module_path, "exceptions"])
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

    def test_eaccpf_getDigitalObjects_with_markup_in_title(self):
        """
        Some EAC-CPF documents have digital objects that have markup in their
        titles. The function should return the title string without markup
        included.
        """
        test_data = os.sep.join([self.module_path, "exceptions", "eac"])
        cases = [
            (test_data + os.sep + "E000007.xml",
             "http://www.asmp.esrc.unimelb.edu.au/eac/E000007.xml",
             "http://www.asmp.esrc.unimelb.edu.au/biogs/E000007b.htm",
             "Map of the Discoveries in Australia, 1834/1 (1832)"),
            (test_data + os.sep + "E000021.xml",
             "http://www.asmp.esrc.unimelb.edu.au/eac/E000021.xml",
             "http://www.asmp.esrc.unimelb.edu.au/biogs/E000021b.htm",
             "Discoveries in Western Australia, 1833/6 (1838/1)"),
        ]
        for case in cases:
            source, metadata_url, presentation_url, expected = case
            doc = EacCpf.EacCpf(source, metadata_url, presentation_url)
            result = doc.getThumbnail()
            self.assertEqual(expected, result.getTitle())

    def test_htmlpage_get_title_with_markup(self):
        """
        Some HTML documents have title strings that include HTML markup. The
        function should return the title string without markup included.
        """
        test_data = os.sep.join([self.module_path, "exceptions"])
        cases = [
            (test_data, "D0000813.htm", "Text - Melbourne and Mars : my mysterious life on two planets : extracts from the diary of a Melbourne merchant - Colonial Australian Popular Fiction"),
            (test_data, "D00000006.htm", "Map - Map of the Discoveries in Australia, 1834/1 (1832) - Arrowsmith's Australian Maps"),
            (test_data, "D0000116.htm", "Map - Discoveries in Western Australia, 1833/6 (1838/1) - Arrowsmith's Australian Maps"),
        ]
        for case in cases:
            path, filename, expected = case
            doc = HtmlPage.HtmlPage(path, filename=filename)
            self.assertNotEqual(None, doc)
            result = doc.getTitle()
            self.assertEqual(expected, result)


if __name__ == "__main__":
    unittest.main()

