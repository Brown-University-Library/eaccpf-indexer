'''
This file is subject to the terms and conditions defined in the
'LICENSE.txt' file, which is part of this source code package.
'''

import logging
from geopy import geocoders
import AlchemyAPI

class Factor():
    '''
    Takes a place name and attempts to return geographic coordinates.
    '''

    def __init__(self,params):
        '''
        Initialize geocoder, Alchemy web service interface.
        '''
        self.logger = logging.getLogger('Factor')

        # create a geocoder
        self.geocoder = geocoders.Google(domain='maps.google.com.au')
        # Create an AlchemyAPI object, load API key
        self.alchemy = AlchemyAPI.AlchemyAPI() 
        self.alchemyObj.loadAPIKey("alchemy_api_key.txt")
        
    def getEntities(self):
        # Extract a ranked list of named entities from a web URL.
        result = self.alchemyObj.URLGetRankedNamedEntities("http://www.techcrunch.com/");
        self.logger.info(result)

        # Extract a ranked list of named entities from a text string.
        result = self.alchemyObj.TextGetRankedNamedEntities("Hello my name is Bob.  I am speaking to you at this very moment.  Are you listening to me, Bob?");
        self.logger.info(result)

        # Load a HTML document to analyze.
        htmlFileHandle = open("data/example.html", 'r')
        htmlFile = htmlFileHandle.read()
        htmlFileHandle.close()

        # Extract a ranked list of named entities from a HTML document.
        result = self.alchemyObj.HTMLGetRankedNamedEntities(htmlFile, "http://www.test.com/");
        self.logger.info(result)

    def getGeoCoordinates(self,PlaceName):
        '''
        Attempt to resolve a place name or address to geographic coordinates. 
        Returns None if geographic coordinates can not be found. Otherwise, it 
        returns a tuple of latitude and longitude values.
        '''
        return self.geocoder.geocode(PlaceName)
    
    def run(self, params):
        self.logger.info("Starting semantic entity extraction")

    