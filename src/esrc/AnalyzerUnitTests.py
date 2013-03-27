'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

import Analyzer
import unittest

class AnalyzerUnitTests(unittest.TestCase):
    '''
    Unit tests for Analyzer module.
    '''

    def setUp(self):
        '''
        Setup the test environment.
        '''
        pass

    def tearDown(self):
        '''
        Tear down the test environment.
        '''
        pass

    def test_init(self):
        '''
        '''
        analyzer = Analyzer()
        self.assertNotEqual(analyzer, None)

if __name__ == "__main__":
    unittest.main()