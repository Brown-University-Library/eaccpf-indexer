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


class TestEacCpf(unittest.TestCase):
    """
    Unit tests for EacCpf module.
    """

    def setUp(self):
        """
        Setup the test environment.
        """
        module_path = os.path.abspath(inspect.getfile(self.__class__))
        self.log = logging.getLogger()
        self.path = os.path.dirname(module_path) + os.sep + 'test' + os.sep + 'eaccpf'
        self.temp = tempfile.mkdtemp()

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
                 'http://www.findandconnect.gov.au/nsw/eac/NE00416.xml':'http://www.findandconnect.gov.au/nsw/biogs/NE00416b.htm',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00123.xml':'http://www.findandconnect.gov.au/nsw/biogs/NE00123b.htm',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00203.xml':'http://www.findandconnect.gov.au/nsw/biogs/NE00203b.htm',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00205.xml':'http://www.findandconnect.gov.au/nsw/biogs/NE00205b.htm',
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
                 'http://www.findandconnect.gov.au/nsw/eac/NE00416.xml':'NE00416',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00123.xml':'NE00123',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00203.xml':'NE00203',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00205.xml':'NE00205',
                  }
        for case in cases:
            doc = EacCpf.EacCpf(case, 'http://www.example.com/metadata.xml', 'http://www.example.com/presentation.html')
            self.assertNotEqual(doc, None)
            abstract = doc.getAbstract()
            self.assertNotEqual(abstract, None)

    def test_getDigitalObject(self):
        """
        It should take an individual digital object relation and retrieve the
        digital object, then build a digital object metadata record.
        """
        cases = {
                 'http://www.findandconnect.gov.au/nsw/eac/NE00416.xml':'NE00416',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00123.xml':'NE00123',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00203.xml':'NE00203',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00205.xml':'NE00205',
                  }
        for case in cases:
            doc = EacCpf.EacCpf(case, 'http://www.example.com/metadata.xml', 'http://www.example.com/presentation.html')
            self.assertNotEqual(doc, None)
    
    def test_getDigitalObjects(self):
        """
        It should get the list of digital objects in the EAC-CPF document.
        """
        cases = {
                 "http://www.findandconnect.gov.au/nsw/" : 0,
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00200b.htm" : 1,
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00280b.htm" : 3,
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00124b.htm" : 1,
                 "http://www.findandconnect.gov.au/nsw/biogs/NE01217b.htm" : 1,
                 "http://www.findandconnect.gov.au/nsw/browse_h.htm": 0,
                 }
        for case in cases:
            html = HtmlPage(case)
            if html.hasEacCpfAlternate():
                url = html.getEacCpfUrl()
                doc = EacCpf.EacCpf(url, 'http://www.example.com')
                self.assertNotEqual(doc, None)
                objects = doc.getDigitalObjects()
                self.assertNotEqual(objects, None)
                self.assertEqual(len(objects), cases[case])
            else:
                self.assertEqual(0, cases[case])

    def test_getEntityType(self):
        """
        It should get the record entity type.
        """
        cases = {
                 "http://www.findandconnect.gov.au/nsw/eac/NE00280.xml":"corporateBody",
                 "http://www.findandconnect.gov.au/nsw/eac/NE00124.xml":"corporateBody",
                 "http://www.findandconnect.gov.au/nsw/eac/NE01217.xml":"corporateBody",
                 }
        for case in cases:
            doc = EacCpf.EacCpf(case, 'http://www.example.com')
            self.assertNotEqual(doc, None)
            entitytype = doc.getEntityType()
            self.assertNotEqual(entitytype, None)
            self.assertEqual(entitytype, cases[case])

    def test_getExistDates(self):
        """
        It should return the entity exist dates in ISO format. If the exist
        date has a standardDate attribute, the standardDate attribute value
        should be returned instead of the date value.
        """
        cases = {
                 "http://www.findandconnect.gov.au/nsw/eac/NE00280.xml":("1900-01-01T00:00:00Z", None),
                 "http://www.findandconnect.gov.au/nsw/eac/NE00124.xml":("1926-01-01T00:00:00Z", None),
                 "http://www.findandconnect.gov.au/vic/eac/E000582.xml":("1942-01-01T00:00:00Z","1965-12-31T00:00:00Z")
                 }
        for case in cases:
            doc = EacCpf.EacCpf(case, 'http://www.example.com')
            self.assertNotEqual(doc, None)
            fromDate, toDate = doc.getExistDates()
            expectFromDate, expectToDate = cases[case]
            self.assertEqual(fromDate, expectFromDate)
            self.assertEqual(toDate, expectToDate)

    def test_getFilename(self):
        """
        It should return the file name from the URL.
        """
        cases = {
                 'http://www.findandconnect.gov.au/nsw/eac/NE00416.xml':'NE00416.xml',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00123.xml':'NE00123.xml',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00203.xml':'NE00203.xml',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00205.xml':'NE00205.xml',
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
        cases = {
                 "http://www.findandconnect.gov.au/nsw/eac/NE00280.xml": 4,
                 "http://www.findandconnect.gov.au/nsw/eac/NE00124.xml": 3,
                 "http://www.findandconnect.gov.au/nsw/eac/NE01217.xml": 4,
                 }
        for case in cases:
            doc = EacCpf.EacCpf(case,'http://www.example.com')
            self.assertNotEqual(doc, None)
            functions = doc.getFunctions()
            self.assertNotEqual(functions, None)
            self.assertEqual(len(functions), cases[case])

    def test_getId(self):
        """
        It should return the entity identifier from the URL or filename.
        """
        cases = {
                 'http://www.findandconnect.gov.au/nsw/eac/NE00416.xml':'NE00416',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00123.xml':'NE00123',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00203.xml':'NE00203',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00205.xml':'NE00205',
                  }
        for case in cases:
            doc = EacCpf.EacCpf(case, 'http://www.example.com/metadata.xml', 'http://www.example.com/presentation.html')
            self.assertNotEqual(doc, None)
            self.assertEquals(doc.getRecordId(), cases[case])

    def test_getLocalType(self):
        """
        It should get the record entity type.
        """
        cases = {
                 "http://www.findandconnect.gov.au/nsw/eac/NE00280.xml": "Organisation",
                 "http://www.findandconnect.gov.au/nsw/eac/NE00124.xml": "Organisation",
                 "http://www.findandconnect.gov.au/nsw/eac/NE01217.xml": "Organisation",
                 }
        for case in cases:
            doc = EacCpf.EacCpf(case,'http://www.example.com')
            self.assertNotEqual(doc, None)
            localtype = doc.getLocalType()
            self.assertEqual(localtype, cases[case])

    def test_getLocations(self):
        """
        It should return a list of locations for the entity. If there are no
        locations available then it should return an empty list. Each location
        record should include the place name, and optional existence dates and
        event description.
        """
        cases = {
                 "http://www.findandconnect.gov.au/nsw/eac/NE00280.xml": 3,
                 "http://www.findandconnect.gov.au/nsw/eac/NE00124.xml": 0,
                 "http://www.findandconnect.gov.au/nsw/eac/NE01217.xml": 1,
                 }
        for case in cases:
            doc = EacCpf.EacCpf(case,'http://www.example.com')
            self.assertNotEqual(doc, None)
            locations = doc.getLocations()
            self.assertNotEqual(locations, None)
            self.assertEqual(cases[case], len(locations))

    def test_getThumbnail(self):
        """
        It should return a digital object representing a thumbnail image for 
        the record, if one is available.
        """
        cases = {
                 "E000001.xml": False,
                 "E000002.xml": True,
                 "E000003.xml": False,
                 "E000004.xml": False,
                 "E000005.xml": True,
                 "E000006.xml": True,
                 }
        files = os.listdir(self.path)
        files.sort()
        for filename in files:
            if filename in cases:
                doc = EacCpf.EacCpf(self.path + os.sep + filename,'http://www.findandconnect.gov.au')
                self.assertNotEqual(doc, None)
                thumb = doc.getThumbnail()
                if thumb != None:
                    self.assertEqual(True, cases[filename])
                else:
                    self.assertEqual(False, cases[filename])

    def test_hasLocation(self):
        """
        It should return true if the record has a location entry, false
        otherwise.
        """
        cases = {
                 "http://www.findandconnect.gov.au/nsw/eac/NE00280.xml": True,
                 "http://www.findandconnect.gov.au/nsw/eac/NE00124.xml": False,
                 "http://www.findandconnect.gov.au/nsw/eac/NE01217.xml": True,
                 }
        for case in cases:
            doc = EacCpf.EacCpf(case,'http://www.example.com')
            self.assertNotEqual(doc, None)
            location = doc.hasLocation()
            self.assertNotEqual(location, None)
            self.assertEqual(cases[case], location)

    def test_write(self):
        """
        It should write out the eac-cpf document to the specified file system
        path. The output document should include additional attributes in the
        root element for the metadata and presentation source URLs.
        """
        cases = {
                 "http://www.findandconnect.gov.au/nsw/eac/NE00280.xml": True,
                 "http://www.findandconnect.gov.au/nsw/eac/NE00124.xml": False,
                 "http://www.findandconnect.gov.au/nsw/eac/NE01217.xml": True,
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