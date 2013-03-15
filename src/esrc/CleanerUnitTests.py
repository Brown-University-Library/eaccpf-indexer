'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

import unittest
import Cleaner

class CleanerUnitTests(unittest.TestCase):
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
        cleaner = Cleaner()
        self.assertNotEqual(cleaner, None)
    
if __name__ == '__main__':
    unittest.main()

    