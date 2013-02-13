'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

import unittest
from Crawler import Crawler

class CrawlerUnitTests(unittest.TestCase):
    '''
    Test cases for the Crawler module
    '''
    
    def setUp(self):
        '''
        Setup the test
        '''
        # load schemas
        # load test data
        # create a temporary directory
        pass
    
    def suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(CleanerUnitTests))
        return suite
    
    def TestClean(self):
        pass
    
    def testRun(self):
        pass
    
    def testValidate(self):
        pass
    
    if __name__ == '__main__':
        suiteFew = unittest.TestSuite()
        suiteFew.addTest(testBlogger("testPostNewEntry"))
        suiteFew.addTest(testBlogger("testDeleteAllEntries"))
        unittest.TextTestRunner(verbosity=2).run(suite())
