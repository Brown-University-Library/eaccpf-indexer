'''
This file is subject to the terms and conditions defined in the
'LICENSE.txt' file, which is part of this source code package.
'''

import logging 

class Transformer(object):
    '''
    Transforms an XML file using an external XSLT transform.
    '''

    def __init__(self,params):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('feeder')
        
    def run(self, params):
        pass
    
    def transform(self, source, output, report=None):
        pass
    
    def validate(self, source, output, schema, report=None):
        pass
    
    