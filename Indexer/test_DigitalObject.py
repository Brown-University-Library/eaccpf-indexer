"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

import DigitalObject
import logging
import inspect
import os
import unittest


class TestDigitalObject(unittest.TestCase):
    """
    Unit tests for DigitalObject module.
    """

    def setUp(self):
        """
        Setup the test environment.
        """
        module = os.path.abspath(inspect.getfile(self.__class__))
        module_path = os.path.dirname(module)
        self.log = logging.getLogger()
        self.test_site = os.sep.join([module_path, "test", "test_site"])
        self.test_eac = self.test_site + os.sep + 'eac' + os.sep
        # sample metadata for digital object
        self.sample_do_1 = {
            "Source": self.test_eac + "NE00301.xml",
            "MetadataUrl":"http://www.findandconnect.gov.au/eac/NE00301.xml",
            "PresentationUrl":"http://www.findandconnect.gov.au/objects/ND0000002.htm",
            "Title":"Title",
            "Abstract":"Abstract",
            "LocalType":"LocalType"
        }
        self.sample_do_2 = {
            "Source": self.test_eac + "NE01101.xml",
            "MetadataUrl":"http://www.findandconnect.gov.au/eac/NE01101.xml",
            "PresentationUrl":"http://www.findandconnect.gov.au/objects/ND0000001.htm",
            "Title":"Title",
            "Abstract":"Abstract",
            "LocalType":"Organisation"
        }

    def tearDown(self):
        """
        Tear down the test environment.
        """
        pass

    def test__init__(self):
        """
        It should return a digital object instance. The operation should always
        succeed.
        """
        cases = [
            self.sample_do_1,
            self.sample_do_2,
        ]
        for case in cases:
            obj = DigitalObject.DigitalObject(**case)
            self.assertNotEqual(obj, None)

    def test_getAbstract(self):
        """
        It should return the digital object abstract.
        """
        cases = [
            (self.sample_do_1, self.sample_do_1['Abstract']),
            (self.sample_do_2, self.sample_do_2['Abstract']),
        ]
        for case in cases:
            args, expected = case
            obj = DigitalObject.DigitalObject(**args)
            result = obj.getAbstract()
            self.assertNotEqual(None, result)
            self.assertEqual(expected, result)

    def test_getFileName(self):
        """
        It should return the source entity filename.
        """
        cases = [
            (self.sample_do_1, 'NE00301.xml'),
            (self.sample_do_2, 'NE01101.xml')
        ]
        for case in cases:
            args, expected = case
            obj = DigitalObject.DigitalObject(**args)
            result = obj.getFileName()
            self.assertNotEqual(None, result)
            self.assertEqual(expected, result)

    def test_getLocalType(self):
        """
        It should return the source entity LocalType value.
        """
        cases = [
            (self.sample_do_1, 'LocalType'),
            (self.sample_do_2, 'Organisation'),
        ]
        for case in cases:
            args, expected = case
            obj = DigitalObject.DigitalObject(**args)
            result = obj.getLocalType()
            self.assertNotEqual(None, result)
            self.assertEqual(expected, result)

    def test_getMetadataUrl(self):
        """
        It should return the URL to the source EAC-CPF document.
        """
        cases = [
            (self.sample_do_1, self.sample_do_1['MetadataUrl']),
            (self.sample_do_2, self.sample_do_2['MetadataUrl']),
        ]
        for case in cases:
            args, expected = case
            obj = DigitalObject.DigitalObject(**args)
            result = obj.getMetadataUrl()
            self.assertNotEqual(None, result)
            self.assertEqual(expected, result)

    def test_getObjectId(self):
        """
        It should return the identifier for the digital object.
        """
        cases = [
            (self.sample_do_1, "ND0000002"),
            (self.sample_do_2, "ND0000001"),
        ]
        for case in cases:
            args, expected = case
            obj = DigitalObject.DigitalObject(**args)
            result = obj.getObjectId()
            self.assertNotEqual(None, result)
            self.assertEqual(expected, result)

    def test_getPresentationUrl(self):
        """
        It should return the URL to the HTML presentation page for the digital
        object.
        """
        cases = [
            (self.sample_do_1, self.sample_do_1['PresentationUrl']),
            (self.sample_do_2, self.sample_do_2['PresentationUrl']),
        ]
        for case in cases:
            args, expected = case
            obj = DigitalObject.DigitalObject(**args)
            result = obj.getPresentationUrl()
            self.assertNotEqual(None, result)
            self.assertEqual(expected, result)

    def test_getRecord(self):
        """
        It should return a dictionary with the digital object properties.
        """
        cases = [
            self.sample_do_1,
            self.sample_do_2,
        ]
        for case in cases:
            obj = DigitalObject.DigitalObject(**case)
            result = obj.getRecord()
            self.assertNotEqual(None, result)
            self.assertEqual(True, isinstance(result, dict))

    def test_getRecordId(self):
        """
        It should return the identifier for the source entity record.
        """
        cases = [
            (self.sample_do_1, "NE00301"),
            (self.sample_do_2, "NE01101")
        ]
        for case in cases:
            args, expected = case
            obj = DigitalObject.DigitalObject(**args)
            result = obj.getRecordId()
            self.assertNotEqual(None, result)
            self.assertEqual(expected, result)

    def test_getSourceUrl(self):
        """
        It should return a URL to the source digital object file.
        """
        cases = [
            (self.sample_do_1, self.test_site + "/nsw/objects/thumbs/tn_Church of England Girls Home.png"),
            (self.sample_do_2, self.test_site + "/nsw/objects/thumbs/tn_CofEBoysCarlingford.png")
        ]
        for case in cases:
            args, expected = case
            obj = DigitalObject.DigitalObject(**args)
            result = obj.getSourceUrl()
            self.assertNotEqual(None, result)
            self.assertEqual(expected, result)

    def test_getType(self):
        """
        It should determine whether a resource specified by a URL is one of 
        image, video or other.
        """
        cases = [
            (self.sample_do_1, "image"),
            (self.sample_do_2, "image")
        ]
        for case in cases:
            args, expected = case
            obj = DigitalObject.DigitalObject(**args)
            result = obj.getType()
            self.assertNotEqual(None, result)
            self.assertEqual(expected, result)

    def test_write(self):
        """
        It should write the digital object metadata in YAML format to the
        specified path.
        """
        pass


if __name__ == "__main__":
    unittest.main()
