'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

import unittest
import Crawler

class CrawlerUnitTests(unittest.TestCase):
    '''
    Test cases for the Crawler module.
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
        crawler = Crawler()
        self.assertNotEqual(crawler, None)
    
if __name__ == '__main__':
    unittest.main()

    