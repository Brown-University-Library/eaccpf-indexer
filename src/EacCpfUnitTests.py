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
        self.cases = {'E000001.xml':0,
                      'E000002.xml':0,
                      'E000003.xml':0,
                      'E000004.xml':0,
                      'E000005.xml':0,
                      'E000006.xml':0,
                      'E000007.xml':0,
                      'E000008.xml':0,
                      'E000009.xml':0,
                      }

    def tearDown(self):
        '''
        Tear down the test environment.
        '''
        pass

    def test___init__(self):
        '''
        It should create an instance of the class and have loaded the file 
        data.
        '''
        for casename in self.cases.keys():
            doc = EacCpf(self.path + os.sep + casename)
            self.assertNotEqual(doc, None)
            self.assertNotEqual(doc.data, None)

    def test__getDataType(self):
        '''
        It should determine whether a resource specified by a URL is one of 
        image, video or other.
        '''
        doc = EacCpf("http://www.findandconnect.gov.au/nsw/eac/NE00280.xml")
        cases = {
                 "http://www.findandconnect.gov.au/":"other",
                 "http://www.findandconnect.gov.au/nsw/eac/NE01217.xml":"other",
                 "http://www.findandconnect.gov.au/nsw/site/images/logo-nsw.png":"image",
                 "http://www.findandconnect.gov.au/nsw/objects/thumbs/tn_Mowbray%20Park.png":"image",
                 "http://www.findandconnect.gov.au/nsw/site/images/external-link.gif":"image",
                 }
        for case in cases:
            datatype = doc._getDigitalObjectType(case)
            self.assertEquals(datatype,cases[case])

    def test__getDateRange(self):
        '''
        It should parse a unitdate and produce valid fromDate and toDate 
        values.
        '''
        doc = EacCpf("http://www.findandconnect.gov.au/nsw/eac/NE00280.xml")
        cases = {
                 '':''
                 }
        for case in cases:
            fromDate, toDate = doc._getDateRange(case)
            self.assertNotEqual(fromDate,toDate)

    def test__getFilename(self):
        '''
        It should return the file name from the URL.
        '''
        doc = EacCpf("http://www.findandconnect.gov.au/nsw/eac/NE00280.xml")
        cases = {
                 '':''
                 }
        for case in cases:
            filename = doc._getFileName(case)
            self.assertNotEqual(filename, None)
            self.assertEquals(filename,cases[case])
    
    def test__getId(self):
        '''
        It should return the entity identifier from the URL or filename.
        '''
        doc = EacCpf("http://www.findandconnect.gov.au/nsw/eac/NE00280.xml")
        cases = {
                 '':''
                 }
        for case in cases:
            docid = doc._getId(case)
            self.assertNotEqual(docid, None)
            self.assertEquals(docid,cases[case])

    def test_getDigitalObject(self):
        '''
        It should take an individual digital object relation and retrieve the
        digital object, then build a digital object metadata record.
        '''
        cases = {
                 "http://www.findandconnect.gov.au/nsw/eac/NE00280.xml": 3,
                 "http://www.findandconnect.gov.au/nsw/eac/NE00124.xml": 0,
                 "http://www.findandconnect.gov.au/nsw/eac/NE01217.xml" : 1,
                 }
        for case in cases:
            doc = EacCpf(case)
            self.assertNotEqual(doc,None)
            objects = doc.getDigitalObjects()
            self.assertNotEqual(objects,None)
            self.assertEqual(len(objects),cases[case])
    
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
                doc = EacCpf(url)
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
            doc = EacCpf(case)
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
            doc = EacCpf(case)
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
            doc = EacCpf(case)
            self.assertNotEqual(doc,None)
            localtype = doc.getLocalType()
            self.assertEqual(localtype,cases[case])

if __name__ == "__main__":
    unittest.main()