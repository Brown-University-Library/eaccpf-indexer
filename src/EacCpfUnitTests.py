'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from EacCpf import EacCpf
from HtmlPage import HtmlPage

import inspect
import os
import unittest

class EacCpfUnitTests(unittest.TestCase):
    '''
    Unit tests for EacCpf module.
    '''

    def setUp(self):
        '''
        Setup the test environment.
        '''
        modulepath = os.path.abspath(inspect.getfile(self.__class__))
        self.path = os.path.dirname(modulepath) + os.sep + 'test' + os.sep + 'eaccpf'

    def tearDown(self):
        '''
        Tear down the test environment.
        '''
        pass

    def test___init__(self):
        '''
        It should create an instance of the class and load the file data.
        '''
        cases = {
                 'http://www.findandconnect.gov.au/nsw/eac/NE00416.xml':'http://www.findandconnect.gov.au/nsw/biogs/NE00416b.htm',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00123.xml':'http://www.findandconnect.gov.au/nsw/biogs/NE00123b.htm',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00203.xml':'http://www.findandconnect.gov.au/nsw/biogs/NE00203b.htm',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00205.xml':'http://www.findandconnect.gov.au/nsw/biogs/NE00205b.htm',
                  }
        for case in cases:
            doc = EacCpf(case,'http://www.example.com')
            self.assertNotEqual(doc, None)
            self.assertNotEqual(doc.data, None)

    def test__getFilename(self):
        '''
        It should return the file name from the URL.
        '''
        cases = {
                 'http://www.findandconnect.gov.au/nsw/eac/NE00416.xml':'NE00416.xml',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00123.xml':'NE00123.xml',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00203.xml':'NE00203.xml',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00205.xml':'NE00205.xml',
                  }
        for case in cases:
            doc = EacCpf(case,'http://www.example.com')
            filename = doc.getFileName()
            self.assertNotEqual(filename, None)
            self.assertEquals(filename,cases[case])
    
    def test__getId(self):
        '''
        It should return the entity identifier from the URL or filename.
        '''
        cases = {
                 'http://www.findandconnect.gov.au/nsw/eac/NE00416.xml':'NE00416',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00123.xml':'NE00123',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00203.xml':'NE00203',
                 'http://www.findandconnect.gov.au/nsw/eac/NE00205.xml':'NE00205',
                  }
        for case in cases:
            doc = EacCpf(case,'http://www.example.com')
            self.assertNotEqual(doc, None)
            self.assertEquals(doc.getRecordId(),cases[case])

    def test_getDigitalObject(self):
        '''
        It should take an individual digital object relation and retrieve the
        digital object, then build a digital object metadata record.
        '''
        pass
    
    def test_getDigitalObjects(self):
        '''
        It should get the list of digital objects in the EAC-CPF document.
        '''
        cases = {
                 "http://www.findandconnect.gov.au/nsw/" : 0,
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00200b.htm" : 1,
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00280b.htm" : 3,
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00124b.htm" : 0,
                 "http://www.findandconnect.gov.au/nsw/biogs/NE01217b.htm" : 1,
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00124b.htm" : 0,
                 "http://www.findandconnect.gov.au/nsw/browse_h.htm": 0,
                 }
        for case in cases:
            html = HtmlPage(case)
            if html.hasEacCpfAlternate():
                url = html.getEacCpfUrl()
                doc = EacCpf(url,'http://www.example.com')
                self.assertNotEqual(doc,None)
                objects = doc.getDigitalObjects()
                self.assertNotEqual(objects,None)
                self.assertEqual(len(objects),cases[case])
            else:
                self.assertEqual(0,cases[case])

    def test_getEntityType(self):
        '''
        It should get the record entity type.
        '''
        cases = {
                 "http://www.findandconnect.gov.au/nsw/eac/NE00280.xml":"corporateBody",
                 "http://www.findandconnect.gov.au/nsw/eac/NE00124.xml":"corporateBody",
                 "http://www.findandconnect.gov.au/nsw/eac/NE01217.xml":"corporateBody",
                 }
        for case in cases:
            doc = EacCpf(case,'http://www.example.com')
            self.assertNotEqual(doc,None)
            entitytype = doc.getEntityType()
            self.assertNotEqual(entitytype,None)
            self.assertEqual(entitytype,cases[case])

    def test_getFunctions(self):
        '''
        It should get the record functions.
        '''
        cases = {
                 "http://www.findandconnect.gov.au/nsw/eac/NE00280.xml": 4,
                 "http://www.findandconnect.gov.au/nsw/eac/NE00124.xml": 3,
                 "http://www.findandconnect.gov.au/nsw/eac/NE01217.xml" : 4,
                 }
        for case in cases:
            doc = EacCpf(case,'http://www.example.com')
            self.assertNotEqual(doc,None)
            functions = doc.getFunctions()
            self.assertNotEqual(functions,None)
            self.assertEqual(len(functions),cases[case])

    def test_getLocalType(self):
        '''
        It should get the record entity type.
        '''
        cases = {
                 "http://www.findandconnect.gov.au/nsw/eac/NE00280.xml": "Organisation",
                 "http://www.findandconnect.gov.au/nsw/eac/NE00124.xml": "Organisation",
                 "http://www.findandconnect.gov.au/nsw/eac/NE01217.xml" : "Organisation",
                 }
        for case in cases:
            doc = EacCpf(case,'http://www.example.com')
            self.assertNotEqual(doc,None)
            localtype = doc.getLocalType()
            self.assertEqual(localtype,cases[case])

if __name__ == "__main__":
    unittest.main()