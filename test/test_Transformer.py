"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from Indexer import Transformer
from lxml import etree

import inspect
import os
import random
import re
import shutil
import string
import tempfile
import unittest


class TestTransformer(unittest.TestCase):
    """
    Executes unit tests against the Transformer module.
    """

    def _generate(self, size=6, chars=string.ascii_uppercase + string.digits):
        """
        Generate a string of random characters.
        """
        return ''.join(random.choice(chars) for _ in range(size))

    def setUp(self):
        """
        Set test environment.
        """
        self.module = os.path.abspath(inspect.getfile(self.__class__))
        self.module_path = os.path.dirname(self.module)
        self.source = self.module_path + os.sep + "transform"
        self.temp = tempfile.mkdtemp()

    def tearDown(self):
        """
        Tear down test environment.
        """
        if os.path.exists(self.temp):
            shutil.rmtree(self.temp, ignore_errors=True)

    def test__init__(self):
        """
        It should create an instance of the Transformer class.
        """
        try:
            t = Transformer.Transformer(self.temp, self.temp)
            self.assertNotEqual(None, t)
        except:
            self.fail("Could not create instance of Transformer class")

    def test_getSourceAndReferrerValues(self):
        """
        Get source and referrer values from the embedded comment in an EAC-CPF 
        document.
        """
        pass

    def test_mergeInferredRecordToSID(self):
        """
        Merge inferred data into Solr Input Document record.
        """
        pass

    def test_setBoosts(self):
        """
        It should set boost values on the specified fields.
        """
        source = self.source + os.sep + "setboosts"
        cases = [
            (['title:1000'], 3),
            (['relation:1000'], 15),
            (['title:1000','relation:1000'], 18),
        ]
        for case in cases:
            boosts, expected_count = case
            t = Transformer.Transformer(self.temp, self.temp, boosts=boosts)
            # copy the test files into the temp folder
            for filename in os.listdir(source):
                shutil.copy(source + os.sep + filename, self.temp)
            # boost the values
            t.setBoosts(self.temp)
            # count the number of instances of boost="value" in the files
            actual_count = 0
            pattern = 'boost="[0-9]*"'
            for filename in os.listdir(self.temp):
                with open(self.temp + os.sep + filename, 'r') as f:
                    data = f.read()
                    matches = re.findall(pattern, data)
                    actual_count += len(matches)
            self.assertEqual(expected_count, actual_count)

    def test_setFields(self):
        """
        It should set the field to the specified value.
        """
        source = self.source + os.sep + "setfields"
        expected = self._generate(size=24)
        cases = [
            (['title:{0}'.format(expected)], ['title']),
            (['relation:{0}'.format(expected)], ['relation']),
            (['relation:{0}'.format(expected),'type:{0}'.format(expected)], ['relation','type']),
        ]
        for case in cases:
            set_fields, fields = case
            t = Transformer.Transformer(self.temp, self.temp, set_fields=set_fields)
            # copy the test files into the temp folder
            for filename in os.listdir(source):
                shutil.copy(source + os.sep + filename, self.temp)
            # boost the field values
            t.setFieldValue(self.temp)
            # ensure that the fields have been set
            for filename in os.listdir(self.temp):
                xml = etree.parse(self.temp + os.sep + filename)
                root = xml.getroot()
                doc = root.getchildren()[0]
                for fieldname in fields:
                    nodes = doc.findall('field[@name="' + fieldname + '"]')
                    for node in nodes:
                        self.assertEqual(expected, node.text)

    def test_transformDigitalObjectToSID(self):
        """
        It should transform a path with digital object YAML records to Solr 
        Input Document format.
        """
        pass

    def test_transformEACCPFToSID(self):
        """
        It should transform a path with EAC-CPF records to Solr Input Document 
        format.
        """
        pass

    def test_missing_source_folders(self):
        """
        It should not throw an exception when the source folders are missing,
        but it should generate a log entry to note the absent folder.
        """
    
if __name__ == "__main__":
    unittest.main()
