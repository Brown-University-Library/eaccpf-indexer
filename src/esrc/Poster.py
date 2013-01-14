'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

import logging 

class Poster():
    '''
    Posts Solr Input Documents to a Solr core. Performs flush, commit and 
    optimize commands. 
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('Poster')
    
    def run(self,params):
        self.logger.info("Starting post operation")
