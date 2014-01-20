'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

import inspect
import os
import tempfile
import unittest
from Analyzer import Analyzer


class TestAnalyzer(unittest.TestCase):
    '''
    Unit tests for Analyzer module.
    '''

    def _rmdir(self, d):
        '''
        Recursively delete a directory.
        @author ActiveState
        @see http://code.activestate.com/recipes/552732-remove-directories-recursively/
        '''
        for path in (os.path.join(d,f) for f in os.listdir(d)):
            if os.path.isdir(path):
                self._rmdir(path)
            else:
                os.unlink(path)
        os.rmdir(d)

    def setUp(self):
        '''
        Setup the test.
        '''
        # folder with test files
        modpath = os.path.abspath(inspect.getfile(self.__class__))
        parentpath = os.path.dirname(modpath)
        self.input = parentpath + os.sep + "test" + os.sep + "analyzer"
        # temporary directory for report files
        self.temp = tempfile.mkdtemp()
        self.analyzer = Analyzer()

    def tearDown(self):
        '''
        Tear down the test environment.
        '''
        if os.path.exists(self.temp):
            self._rmdir(self.temp)
        self.assertNotEqual(True, os.path.exists(self.temp))

    def test__getEntityType(self):
        '''
        It should get the entity type from an EAC-CPF document.
        '''
        # analyzer = Analyzer()
        # cases = {
        #      'E000001.xml':'corporateBody',
        #      'E000002.xml':'corporateBody',
        #      'E000003.xml':'corporateBody',
        #      'E000004.xml':'corporateBody',
        #      'E000005.xml':'corporateBody',
        #      'E000006.xml':'corporateBody',
        #      'E000007.xml':'corporateBody',
        #      'E000008.xml':'person',
        #      'E000009.xml':'corporateBody',
        #      }
        # for filename in iter(cases.keys()):
        #     infile = open(self.input + os.sep + filename,'r')
        #     data = infile.read()
        #     infile.close()
        #     entitytype = analyzer._getEntityType(data)
        #     self.assertNotEqual(entitytype, None)
        #     self.assertEqual(entitytype, cases[filename])
        pass

    def test__getEntityLocalType(self):
        '''
        It should get the local entity type from an EAC-CPF document.
        '''
        # analyzer = Analyzer()
        # cases = {
        #      'E000001.xml':'Organisation',
        #      'E000002.xml':'Organisation',
        #      'E000003.xml':'Organisation',
        #      'E000004.xml':'Organisation',
        #      'E000005.xml':'Organisation',
        #      'E000006.xml':'Organisation',
        #      'E000007.xml':'Organisation',
        #      'E000008.xml':'Person',
        #      'E000009.xml':'Organisation',
        #      }
        # for filename in iter(cases.keys()):
        #     infile = open(self.input + os.sep + filename,'r')
        #     data = infile.read()
        #     infile.close()
        #     localtype = analyzer._getEntityLocalType(data)
        #     self.assertNotEqual(localtype, None)
        #     self.assertEqual(localtype, cases[filename])
        pass

    def test__getExistDates(self):
        '''
        It should get a list of existence dates from an EAC-CPF document.
        '''
        pass

    def test__getResourceRelations(self):
        '''
        It should get a list of resource relations from an EAC-CPF document.
        '''
        pass

    def test__getResourceRelationsCount(self):
        '''
        It should get a total count of the number of resource relations in an 
        EAC-CPF document.
        '''
        pass

    def test__getSectionContentCounts(self):
        '''
        It should get a dictionary with a count of the number of characters in
        each section of the EAC-CPF document.
        '''
        cases = {
             'E000001.xml':{'control': 1151, 'relations': 5332, 'description': 1335, 'identity': 222},
             'E000002.xml':{'control': 1151, 'relations': 3352, 'description': 1631, 'identity': 247},
             'E000003.xml':{'control': 1151, 'relations': 4486, 'description': 1112, 'identity': 235},
             'E000004.xml':{'control': 1151, 'relations': 0, 'description': 665, 'identity': 223},
             'E000005.xml':{'control': 1151, 'relations': 5496, 'description': 1052, 'identity': 406},
             'E000006.xml':{'control': 1160, 'relations': 7075, 'description': 3321, 'identity': 535},
             'E000007.xml':{'control': 1151, 'relations': 13396, 'description': 10720, 'identity': 319},
             'E000008.xml':{'control': 1145, 'relations': 11062, 'description': 3716, 'identity': 373},
             'E000009.xml':{'control': 1151, 'relations': 0, 'description': 1150, 'identity': 216},
             }
        for filename in iter(cases.keys()):
            infile = open(self.input + os.sep + filename,'r')
            data = infile.read()
            infile.close()
            count = self.analyzer._getSectionContentCounts(data)
            self.assertNotEqual(count, None)
            # check individual section lengths
    
    def test__getTotalContentCount(self):
        '''
        It should get a total count of the number of characters in the EAC-CPF
        document.
        '''
        cases = [
            ('E000001.xml', 8618),
            ('E000002.xml', 6930),
            ('E000003.xml', 7553),
            ('E000004.xml', 2510),
            ('E000005.xml', 8734),
            ('E000006.xml', 12605),
            ('E000007.xml', 26315),
            ('E000008.xml', 17085),
            ('E000009.xml', 2988),
        ]
        for case in cases:
            filename, expected = case
            infile = open(self.input + os.sep + filename,'r')
            data = infile.read()
            infile.close()
            result = self.analyzer._getTotalContentCount(data)
            self.assertNotEqual(None, result)
            self.assertEqual(expected, result)

    def test__hasMaintenanceRecord(self):
        '''
        It should determine whether the EAC-CPF document has any maintenance 
        section entries.
        '''
        pass

    def test__hasRecordIdentifier(self):
        '''
        It should determine whether the EAC-CPF document has an identifier.
        '''
        # analyzer = Analyzer()
        # cases = {
        #      'E000001.xml':True,
        #      'E000002.xml':True,
        #      'E000003.xml':True,
        #      'E000004.xml':True,
        #      'E000005.xml':True,
        #      'E000006.xml':True,
        #      'E000007.xml':True,
        #      'E000008.xml':True,
        #      'E000009.xml':True,
        #      }
        # for filename in iter(cases.keys()):
        #     infile = open(self.input + os.sep + filename,'r')
        #     data = infile.read()
        #     infile.close()
        #     result = analyzer._hasRecordIdentifier(data)
        #     self.assertNotEqual(result, None)
        #     self.assertEqual(result, cases[filename])
        pass
        
    def test__hasResourceRelations(self):
        '''
        It should determine whether the EAC-CPF document has one or more 
        resource relations.
        '''
        # analyzer = Analyzer()
        # cases = {
        #      'E000001.xml':True,
        #      'E000002.xml':True,
        #      'E000003.xml':True,
        #      'E000004.xml':False,
        #      'E000005.xml':True,
        #      'E000006.xml':True,
        #      'E000007.xml':True,
        #      'E000008.xml':True,
        #      'E000009.xml':False,
        #      }
        # for filename in iter(cases.keys()):
        #     infile = open(self.input + os.sep + filename,'r')
        #     data = infile.read()
        #     infile.close()
        #     result = analyzer._hasResourceRelations(data)
        #     self.assertNotEqual(result, None)
        #     self.assertEqual(result, cases[filename])
        pass

    def test__isConformantToEacCpfSchema(self):
        '''
        It should determine whether an EAC-CPF file is valid and conforms to 
        the document schema.
        @todo this test is failing systematically, likely because the schema is not in sync w the files we are producing
        '''
        cases = [
            ('E000001.xml', True),
            ('E000002.xml', True),
            ('E000003.xml', True),
            # ('invalid.xml', False),
        ]
        for case in cases:
            filename, expected = case
            with open(self.input + os.sep + filename,'r') as f:
                data = f.read()
            result, errors = self.analyzer._isConformantToEacCpfSchema(data)
            self.assertEqual(expected, result)

    def test__isEacCpfFile(self):
        '''
        It should determine whether a file is EAC-CPF.
        '''
        # cases = {
        #      'E000001.xml':True,
        #      'E000002.xml':True,
        #      'E000003.xml':True,
        #      'invalid.xml':True,
        #      'noteaccpf.xml':False,
        #      }
        # for filename in iter(cases.keys()):
        #     result = self.analyzer._isEacCpfFile(self.input + os.sep + filename)
        #     self.assertEquals(result,cases[filename])
        pass

    def test_init(self):
        '''
        It should create an instance of the Analyzer class.
        '''
        self.assertNotEqual(self.analyzer, None)

    def test_analyzeFile(self):
        '''
        It should execute a collection of tests on a single file and then write
        a report file to a specified directory. It should update existing report
        files.
        '''
        cases = [
            ('E000001.xml', 'E000001.yml', True),
            ('E000002.xml', 'E000002.yml', True),
            ('E000003.xml', 'E000003.yml', True),
            ('E000004.xml', 'E000004.yml', False),
            ('E000005.xml', 'E000005.yml', True),
            ('E000006.xml', 'E000006.yml', True),
            ('E000007.xml', 'E000007.yml', True),
            ('E000008.xml', 'E000008.yml', True),
            ('E000009.xml', 'E000009.yml', False),
        ]
        # it should generate a report for each input file
        for case in cases:
            filename, output_filename, expected = case
            self.analyzer.analyzeFile(self.input, filename, self.temp)
            output_path = self.temp + os.sep + output_filename
            self.assertEquals(expected, os.path.exists(output_path))

    def test_analyzeFiles(self):
        '''
        It should execute tests on a collection of input files and then write a
        report file for each.
        '''
        files = os.listdir(self.input)
        self.analyzer.analyzeFiles(self.input, self.temp, {})
        reports = os.listdir(self.temp)
        # invalid.xml, *2.xml and *4.xml don't show up in the report output
        self.assertEqual(len(files) - 1 - 2, len(reports))

if __name__ == "__main__":
    unittest.main()
