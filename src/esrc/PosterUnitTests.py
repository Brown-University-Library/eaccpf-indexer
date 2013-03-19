'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

import os
import random
import string
import tempfile
import unittest
from .Poster import Poster

class PosterUnitTests(unittest.TestCase):
    '''
    Executes unit tests against the Poster module.
    '''

    def _generate(self, size=6, chars=string.ascii_uppercase + string.digits):
        '''
        Generate a string of random characters.
        '''
        return ''.join(random.choice(chars) for _ in range(size))

    def setUp(self):
        '''
        Set test environment.
        '''
        pass

    def tearDown(self):
        '''
        Tear down test environment.
        '''
        pass
    
    def test_init(self):
        '''
        It should create an instance of the Poster class.
        '''
        pass
    
if __name__ == "__main__":
    unittest.main()
