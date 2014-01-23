"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from Indexer import EacCpf
from lxml import etree

import inspect
import logging
import os
import shutil
import tempfile
import unittest


class TestEacCpf(unittest.TestCase):
    """
    Unit tests for EacCpf module.
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
        if os.path.exists(self.temp):
            shutil.rmtree(self.temp)

    def test___init__(self):
        """
        It should create an instance of the class and load the file data.
        """
        cases = {
            self.test_eac + 'NE00001.xml':'http://www.findandconnect.gov.au/ref/nsw/biogs/NE00001b.htm',
            self.test_eac + 'NE00201.xml':'http://www.findandconnect.gov.au/ref/nsw/biogs/NE00201b.htm',
            self.test_eac + 'NE00700.xml':'http://www.findandconnect.gov.au/ref/nsw/biogs/NE00700b.htm',
            self.test_eac + 'NE00915.xml':'http://www.findandconnect.gov.au/ref/nsw/biogs/NE00915b.htm',
        }
        for case in cases:
            doc = EacCpf.EacCpf(case, 'http://www.example.com')
            self.assertNotEqual(doc, None)
            self.assertNotEqual(doc.xml, None)

    def test_getAbstract(self):
        """
        It should return the content of description/biogHist/abstract.
        """
        cases = {
                 self.test_eac + 'NE00001.xml':'NE00001',
                 self.test_eac + 'NE00100.xml':'NE00100',
                 self.test_eac + 'NE00200.xml':'NE00200',
                 self.test_eac + 'NE00600.xml':'NE00600',
        }
        for case in cases:
            doc = EacCpf.EacCpf(case, 'http://www.example.com/metadata.xml', 'http://www.example.com/presentation.html')
            self.assertNotEqual(doc, None)
            abstract = doc.getAbstract()
            self.assertNotEqual(abstract, None)

    def test_getData(self):
        """
        It should return the raw XML source data for the document.
        """
        cases = [
            self.test_eac + 'NE01201.xml',
            self.test_eac + 'NE00201.xml',
            self.test_eac + 'NE00300.xml',
            self.test_eac + 'NE00500.xml',
        ]
        for case in cases:
            doc = EacCpf.EacCpf(case, 'http://www.example.com/metadata.xml', 'http://www.example.com/presentation.html')
            self.assertNotEqual(doc, None)
            result = doc.getData()
            self.assertNotEqual(result, None)
            self.assertGreater(len(result), 0)

    def test_getDigitalObjects(self):
        """
        It should get the list of digital objects in the EAC-CPF document.
        """
        cases = [
            (self.test_eac + 'NE00001.xml', 0),
            (self.test_eac + 'NE00100.xml', 1),
            (self.test_eac + 'NE01101.xml', 15),
            (self.test_eac + 'NE01400.xml', 1),
        ]
        for case in cases:
            source, expected = case
            doc = EacCpf.EacCpf(source, 'http://www.example.com/metadata.xml', 'http://www.example.com/presentation.html')
            self.assertNotEqual(doc, None)
            result = doc.getDigitalObjects()
            self.assertNotEqual(result, None)
            self.assertEqual(len(result), expected)

    def test_getEntityType(self):
        """
        It should get the record entity type.
        """
        cases = [
            (self.test_eac + "NE00001.xml","concept"),
            (self.test_eac + "NE00700.xml","concept"),
            (self.test_eac + "NE01400.xml","corporateBody"),
            (self.test_eac + "NE00301.xml","corporateBody"),
            (self.test_eac + "NE01201.xml","person"),
        ]
        for case in cases:
            source, expected = case
            doc = EacCpf.EacCpf(source, 'http://www.example.com')
            self.assertNotEqual(doc, None)
            result = doc.getEntityType()
            self.assertNotEqual(result, None)
            self.assertEqual(result, expected)

    def test_getExistDates(self):
        """
        It should return the entity exist dates in ISO format. If the exist
        date has a standardDate attribute, the standardDate attribute value
        should be returned instead of the date value.
        """
        cases = [
            (self.test_eac + "NE01201.xml","1858-01-01T00:00:00Z","1935-08-21T00:00:00Z"),
            (self.test_eac + "NE00300.xml","1960-01-01T00:00:00Z","1977-12-31T00:00:00Z"),
            (self.test_eac + "NE01500.xml","1981-01-01T00:00:00Z","1981-12-31T00:00:00Z")
        ]
        for case in cases:
            source, expected_from_date, expected_to_date = case
            doc = EacCpf.EacCpf(source, 'http://www.example.com')
            self.assertNotEqual(doc, None)
            fromDate, toDate = doc.getExistDates()
            self.assertEqual(fromDate, expected_from_date)
            self.assertEqual(toDate, expected_to_date)

    def test_getFilename(self):
        """
        It should return the file name from the URL.
        """
        cases = {
            self.test_eac + 'NE00401.xml':'NE00401.xml',
            self.test_eac + 'NE00001.xml':'NE00001.xml',
            self.test_eac + 'NE00701.xml':'NE00701.xml',
            self.test_eac + 'NE01501.xml':'NE01501.xml',
        }
        for case in cases:
            doc = EacCpf.EacCpf(case, 'http://www.example.com/metadata.xml', 'http://www.example.com/presentation.html')
            filename = doc.getFileName()
            self.assertNotEqual(filename, None)
            self.assertEquals(filename, cases[case])

    def test_getFunctions(self):
        """
        It should get the record functions.
        """
        cases = [
            (self.test_eac + "NE01100.xml", 4),
            (self.test_eac + "NE01101.xml", 8),
            (self.test_eac + "NE01501.xml", 0),
            (self.test_eac + "NE00001.xml", 0),
        ]
        for case in cases:
            source, expected = case
            doc = EacCpf.EacCpf(source, 'http://www.example.com')
            self.assertNotEqual(doc, None)
            result = doc.getFunctions()
            self.assertNotEqual(result, None)
            self.assertEqual(len(result), expected)

    def test_getId(self):
        """
        It should return the entity identifier from the URL or filename.
        """
        cases = [
            (self.test_eac + 'NE00401.xml','NE00401'),
            (self.test_eac + 'NE00101.xml','NE00101'),
            (self.test_eac + 'NE00915.xml','NE00915'),
            (self.test_eac + 'NE01001.xml','NE01001'),
        ]
        for case in cases:
            source, expected = case
            doc = EacCpf.EacCpf(source, 'http://www.example.com/metadata.xml', 'http://www.example.com/presentation.html')
            result = doc.getRecordId()
            self.assertNotEqual(doc, None)
            self.assertEquals(result, expected)

    def test_getLocalType(self):
        """
        It should get the record entity type.
        """
        cases = [
            (self.test_eac + "NE00800.xml", "Archival Series"),
            (self.test_eac + "NE00916.xml", "Archival Collection"),
            (self.test_eac + "NE01201.xml", "Person"),
            (self.test_eac + "NE01000.xml", "Glossary Term"),
        ]
        for case in cases:
            source, expected = case
            doc = EacCpf.EacCpf(source,'http://www.example.com')
            self.assertNotEqual(doc, None)
            result = doc.getLocalType()
            self.assertEqual(result, expected)

    def test_getLocations(self):
        """
        It should return a list of locations for the entity. If there are no
        locations available then it should return an empty list. Each location
        record should include the place name, and optional existence dates and
        event description.
        """
        cases = [
            (self.test_eac + "NE00601.xml", 0),
            (self.test_eac + "NE00100.xml", 1),
            (self.test_eac + "NE00201.xml", 3),
        ]
        for case in cases:
            source, expected = case
            doc = EacCpf.EacCpf(source, 'http://www.example.com')
            self.assertNotEqual(None, doc)
            result = doc.getLocations()
            self.assertNotEqual(None, result)
            self.assertEqual(expected, len(result))

    def test_getThumbnail(self):
        """
        It should return a digital object representing a thumbnail image for 
        the record, if one is available.
        """
        cases = [
            (self.test_eac + 'NE00001.xml', False),
            (self.test_eac + 'NE00100.xml', True),
            (self.test_eac + 'NE01101.xml', True),
            (self.test_eac + 'NE01400.xml', True),
        ]
        for case in cases:
            source, expected = case
            doc = EacCpf.EacCpf(source, 'http://www.findandconnect.gov.au')
            self.assertNotEqual(None, doc)
            result = doc.getThumbnail()
            self.assertEqual(expected, result != None)

    def test_getTitle(self):
        """
        It should return the name for the record. Where the name comprises
        multiple parts, it should return the concatenated title string.
        See issue #30.
        """
        path = os.sep.join([self.module_path, "eaccpf"])
        cases = [
            (path + os.sep + 'markup_in_title_1.xml', "Anglicare Victoria"),
            (path + os.sep + 'markup_in_title_2.xml', "Anglicare Victoria -  Corporate Body"),
            (path + os.sep + 'markup_in_title_3.xml', "Anglicare Victoria (1984/1)"),
            (path + os.sep + 'markup_in_title_4.xml', "Anglicare Victoria (1984/1) -  Corporate Body"),
        ]
        for case in cases:
            source, expected = case
            doc = EacCpf.EacCpf(source, 'http://www.findandconnect.gov.au', 'http://www.findandconnect.gov.au')
            self.assertNotEqual(None, doc)
            result = doc.getTitle()
            self.assertEqual(expected, result)

    def test_hasLocation(self):
        """
        It should return true if the record has a location entry, false
        otherwise.
        """
        cases = [
            (self.test_eac + "NE00601.xml", False),
            (self.test_eac + "NE00100.xml", True),
            (self.test_eac + "NE00201.xml", True),
            (self.test_eac + "NE01302.xml", True),
            (self.test_eac + "NE01101.xml", False),
            (self.test_eac + "NE00916.xml", False),
            (self.test_eac + "NE00201.xml", True),
        ]
        for case in cases:
            source, expected = case
            doc = EacCpf.EacCpf(source,'http://www.example.com')
            self.assertNotEqual(doc, None)
            result = doc.hasLocation()
            self.assertNotEqual(result, None)
            self.assertEqual(result, expected)

    def test_write(self):
        """
        It should write out the eac-cpf document to the specified file system
        path. The output document should include additional attributes in the
        root element for the metadata and presentation source URLs.
        """
        cases = {
            self.test_eac + "NE00401.xml": True,
            self.test_eac + "NE01501.xml": False,
            self.test_eac + "NE01302.xml": True,
        }
        metadata_url = 'http://www.example.com/metadata.xml'
        presentation_url = 'http://www.example.com/presentation.html'
        for case in cases:
            doc = EacCpf.EacCpf(case, metadata_url, presentation_url)
            self.assertNotEqual(doc, None)
            path = doc.write(self.temp)
            self.assertEquals(os.path.exists(path), True)
            # read the file and try to extract the attributes
            try:
                tree = etree.parse(path)
                ns = {
                    EacCpf.DOC_KEY: EacCpf.DOC_NS,
                    EacCpf.ESRC_KEY: EacCpf.ESRC_NS,
                }
                # get the url to the metadata file
                metadata = tree.xpath("//doc:eac-cpf/@" + EacCpf.ESRC_KEY + ":metadata", namespaces=ns)
                self.assertNotEqual(metadata, None)
                self.assertEqual(metadata[0], metadata_url)
                # get the url to the presentation file
                presentation = tree.xpath("//doc:eac-cpf/@" + EacCpf.ESRC_KEY + ":presentation", namespaces=ns)
                self.assertNotEqual(presentation, None)
                self.assertEqual(presentation[0], presentation_url)
                # get the url to the source file
                source = tree.xpath("//doc:eac-cpf/@" + EacCpf.ESRC_KEY + ":source", namespaces=ns)
                self.assertNotEqual(source, None)
                self.assertEqual(source[0], case)
            except:
                msg = "Failed to complete parsing of {0}".format(case)
                self.log.error(msg, exc_info=True)
                self.fail(msg)


if __name__ == "__main__":
    unittest.main()
