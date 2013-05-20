"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

import unittest


from Poster import Poster

class PosterUnitTests(unittest.TestCase):
    """
    Executes unit tests against the Poster module.
    """

    def setUp(self):
        """
        Set up the test environment.
        """
        self.poster = Poster()
        
    def tearDown(self):
        """
        Tear down the test environment.
        """
        pass
    
    def test_init(self):
        """
        It should create an instance of the Poster class.
        """
        self.assertNotEqual(self.poster,None)
        self.assertNotEqual(self.poster.logger,None)
    
    def test__hasRequiredFields(self):
        """
        It should determine whether a Solr Input Document has all the required 
        fields for a specified index.
        """
        cases = {
                 'sid01.xml':True,
                 'sid02.xml':False,
                 'sid03.xml':False,
                 }
        for case in cases:
            pass

if __name__ == "__main__":
    unittest.main()
