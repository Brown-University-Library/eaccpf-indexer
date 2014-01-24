'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from Indexer import Cleaner

import unittest


class TestCleaner(unittest.TestCase):
    '''
    Test cases for the Cleaner module.
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
        It should create an object instance.
        '''
        pass

    def test_clean_eaccpf(self):
        '''
        It should replace HTML encoded entities and other problems typical of
        free text fields.
        '''
        pass
    
    def test_clean_html(self):
        '''
        It should fix errors and common problems found in HTML files, then 
        write a cleaned file to the specified location.
        '''
        pass
    
if __name__ == '__main__':
    unittest.main()

    