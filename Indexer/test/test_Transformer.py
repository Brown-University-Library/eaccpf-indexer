"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from .. import Transformer

import os
import random
import string
import tempfile
import unittest


class TestTransformer(unittest.TestCase):
    """
    Executes unit tests against the transformer module.
    """

    def _generate(self, size=6, chars=string.ascii_uppercase + string.digits):
        """
        Generate a string of random characters.
        """
        return ''.join(random.choice(chars) for _ in range(size))

    def _writeDigitalObject(self, Path):
        """
        Write a minimal digital object record to a file for testing.
        """    
        outfile = open(Path,'w')
        outfile.write('comment: DIGITAL OBJECT record from ????????.xml\n')
        outfile.write('url: http://www.example.com/path/to/source/image.jpg\n')
        outfile.write('path: /path/to/object/0000111100001111.jpg\n')
        outfile.write('cache_id: 00001111000011110000111100001111\n')
        outfile.close()
        return Path
    
    def _writeEACCPF(self, Path):
        """
        Write a minimal EAC-CPF document for testing.
        """
        outfile = open(Path,'w')
        outfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        outfile.write('<eac-cpf>\n')
        outfile.write('<control></control>\n')
        outfile.write('<identity></identity>\n')
        outfile.write('<description></description>\n')
        outfile.write('</eac-cpf>\n')
        outfile.write('<!-- @source=http://www.example.com/NE00054.xml @referrer=http://www.example.com/NE00054b.htm -->')
        outfile.close()
        return Path

    def _writeInferredRecord(self,Path):
        """
        Write a minimal inferred record for testing.
        """
        outfile = open(Path,'w')
        outfile.write('comment: INFERRED DATA record for SOURCE\n')
        outfile.write('locations: \n')
        outfile.write('entities: \n')
        outfile.write('topics: \n')
        outfile.close()
        return Path

    def _writeSolrInputDocument(self,Path):
        """
        Write a minimal Solr Input Document for testing.
        """
        outfile = open(Path,'w')
        outfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        outfile.write('<add>\n')
        outfile.write('<doc>\n')
        outfile.write('<field/>\n')
        outfile.write('</doc></description>\n')
        outfile.write('</add>\n')
        outfile.close()
        return Path

    def setUp(self):
        """
        Set test environment.
        """
        # a junk file
        self.junk = tempfile.mktemp()
        outfile = open(self.junk,'w')
        outfile.write(self._generate(128))
        outfile.close()
        # a junk yml file
        self.yml = tempfile.mktemp(suffix=".yml")
        outfile = open(self.yml,'w')
        outfile.write(self._generate(128))
        outfile.close()
        # a junk xml file
        self.xml = tempfile.mktemp(suffix=".xml")
        outfile = open(self.xml,'w')
        outfile.write(self._generate(128))
        outfile.close()
        # some valid files
        self.digitalObject = self._writeDigitalObject(tempfile.mktemp(suffix=".yml"))
        self.eaccpf = self._writeEACCPF(tempfile.mktemp(suffix=".xml"))
        self.inferred = self._writeInferredRecord(tempfile.mktemp(suffix=".yml"))
        self.solr = self._writeSolrInputDocument(tempfile.mktemp(suffix=".xml"))
        # the test class instance
        self.transformer = Transformer.Transformer()

    def tearDown(self):
        """
        Tear down test environment.
        """
        os.remove(self.junk)
        os.remove(self.yml)
        os.remove(self.xml)
        os.remove(self.digitalObject)
        os.remove(self.eaccpf)
        os.remove(self.inferred)
        os.remove(self.solr)
        self.assertEqual(os.path.exists(self.junk),False)
        self.assertEqual(os.path.exists(self.yml),False)
        self.assertEqual(os.path.exists(self.xml),False)
        self.assertEqual(os.path.exists(self.digitalObject),False)
        self.assertEqual(os.path.exists(self.eaccpf),False)
        self.assertEqual(os.path.exists(self.inferred),False)
        self.assertEqual(os.path.exists(self.solr),False)

    def test_boostFields(self):
        """
        Boost the specified Solr Input Document fields.
        """
        pass

    def test_getSourceAndReferrerValues(self):
        """
        Get source and referrer values from the embedded comment in an EAC-CPF 
        document.
        """
        pass

    def test_init(self):
        """
        It should create an instance of the Transformer class.
        """
        self.assertNotEqual(None, self.transformer)

    def test_mergeInferredRecordToSID(self):
        """
        Merge inferred data into Solr Input Document record.
        """
        pass
    
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
    
if __name__ == "__main__":
    unittest.main()
