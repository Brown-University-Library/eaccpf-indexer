'''
This file is subject to the terms and conditions defined in the
'LICENSE.txt' file, which is part of this source code package.
'''

from BeautifulSoup import BeautifulSoup as soup
from geopy import geocoders
import logging
import os
import AlchemyAPI

class Facter(object):
    '''
    Takes a place name and attempts to return geographic coordinates.
    '''

    def __init__(self):
        '''
        Initialize class
        '''
        self.logger = logging.getLogger('Facter')
        
    def _makeCache(self, path):
        '''
        Create a cache folder at the specified path if none exists.
        If the path already exists, delete all files.
        '''
        if not os.path.exists(path):
            os.makedirs(path)
            self.logger.info("Created output folder at " + path)
        else:
            files = os.listdir(path)
            for afile in files:
                os.remove(path + os.sep + afile)
            self.logger.info("Cleared output folder at " + path)
    
    def inferEntities(self, source, output, report, api_key):
        '''
        For each input file, attempt to extract people, things, concepts
        and place names from free text fields.
        '''
        # Create an AlchemyAPI object, load API key
        self.alchemy = AlchemyAPI.AlchemyAPI() 
        self.alchemyObj.loadAPIKey("alchemy_api_key.txt")
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
        
    def inferLocations(self, source, output, report, geocoder=geocoders.Google(domain='maps.google.com.au'), api_key):
        '''
        For each input file, extract the location name or address and attempt 
        to resolve its geographic coordinates.
        '''
        # create output folder
        self._makeCache(output)
        # check state
        assert os.path.exists(source), self.logger.warning("Specified path does not exist: " + source)
        # process files
        files = os.listdir(source)
        for filename in files:
            # read xml
            infile = open(source + os.sep + filename, 'r')
            data = infile.read()
            xml = soup(data)
            infile.close()
            locations = []
            # for each chronItem
            for chronItem in xml.findAll('chronItem'):
                date = chronItem.find('date')
                place = chronItem.find('place')
                event = chronItem.find('event')
                # if the item does not contain a GIS location value then
                # attempt to infer the geographic coordinates
                if not place.getAttr('GIS'):
                    coordinates = self.geocoder.geocode(place)
                    locations.append(date + ";" + event + ";" + place + ";" + coordinates)
            # write output 
            outfile = open(output + os.sep + filename, 'a')
            outfile.write("## Location data inferred from entity record " + filename)
            for location in locations:
                outfile.write(location)
            outfile.close()
            self.logger.info("Wrote location information to " + filename)

    def run(self, params):
        '''
        Execute semantic analysis and information extraction using the 
        specified parameters.
        '''
        self.logger.info("Starting inference operation")
        # get parameters
        source = params.get("infer","input")
        output = params.get("infer","output")
        report = params.get("infer","report")
        alchemy_api_key = params.get("infer","alchemy_api_key")
        google_api_key = params.get("infer","google_api_key")
        # infer location
        self.inferLocations(source,output,report,api_key=google_api_key)
        # infer entities
        # self.inferEntities(source,output,report,alchemy_api_key)
    