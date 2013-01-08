'''
This file is subject to the terms and conditions defined in the
'LICENSE.txt' file, which is part of this source code package.
'''

import logging

class Reporter():
    '''
    Generates an HTML report on the correctness and quality of a collection of 
    EAC, EAC-CPF files.
    '''

    def __init__(self,params):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('Reporter')
        
    def run(self,params):
        self.logger.info("Starting report generation")