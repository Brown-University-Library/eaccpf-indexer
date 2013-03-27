'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

import logging

class DigitalObject(object):
    '''
    Digital object is an image or video file and associated metadata.
    '''

    def __init__(self, Base=None):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('DigitalObject')
        self.base = Base
        self.record = {}

    def getRecord(self):
        '''
        '''
        return self.record

    def store(self):
        '''
        Store the digital object proxy in the cache.
        '''
        pass
