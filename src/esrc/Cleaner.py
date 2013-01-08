'''
This file is subject to the terms and conditions defined in the
'LICENSE.txt' file, which is part of this source code package.
'''

import logging
import os

class Cleaner():
    '''
    Corrects common errors in XML files and validates the file against an 
    external schema.
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('feeder')

    def clean(self, source, output):
        files = os.listdir(source)
        for f in files:
            pass 
        
    def run(self, params):
        '''
        Execute the operation
        '''
        self.logger.info("Starting clean operation")

    def validate(self, source, schema):
        '''
        Validate a collection of files against an XML Schema.
        '''
        files = os.listdir(source)
        for f in files:
            # validate
            pass 
        
