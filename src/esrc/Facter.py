'''
This file is subject to the terms and conditions defined in the
'LICENSE.txt' file, which is part of this source code package.
'''

from BeautifulSoup import BeautifulSoup as soup
from geopy import geocoders
import AlchemyAPI
import logging
import os
import traceback
import yaml 

class Facter(object):
    '''
    Takes a place name and attempts to return geographic coordinates.
    '''

    def __init__(self):
        '''
        Initialize class
        '''
        self.logger = logging.getLogger('feeder')

    def _cleanList(self, alist):
        '''
        Fix yaml encoding issues for list items.
        '''
        for item in alist:
            item = self._cleanText(item)
        return list

    def _cleanText(self, val):
        '''
        Fix yaml encoding issues for string items.
        '''
        clean = str(val)
        clean = clean.strip()
        # clean = clean.replace('\n','')
        return clean

    def _getRecord(self, path, filename):
        '''
        Try to load the entity record. If it does not already exist, return a
        default dictionary record structure. The record is encoded in YAML 
        format.
        '''
        if os.path.exists(path + os.sep + filename):
            # load the existing record file as yaml
            infile = open(path + os.sep + filename, 'r')
            record = yaml.load(infile)
            infile.close()
            return record
        else:
            # create a default record structure and return it
            return {'entities':[], 'locations':[]}
    
    def _getYamlFilename(self, filename):
        '''
        Takes a file name 
        and returns a name with .yml appended
        '''
        name, _ = os.path.splitext(filename)
        return name + ".yml"
        
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
        
    def inferLocations(self, source, output, report, geocoder, api_key):
        '''
        For each input file, extract the locationName name or address and attempt 
        to resolve its geographic coordinates.
        '''
        # create output folder
        self._makeCache(output)
        # check state
        assert os.path.exists(source), self.logger.warning("Specified path does not exist: " + source)
        # process files
        files = os.listdir(source)
        for filename in files:
            # read source data
            infile = open(source + os.sep + filename, 'r')
            lines = infile.readlines()
            xml = soup(''.join(lines))
            infile.close()
            # get the output record
            yamlFilename = self._getYamlFilename(filename)
            record = self._getRecord(output,yamlFilename)
            # clear the existing locations section before populating
            record['locations'] = []
            # for each chronItem
            for chronItem in xml.findAll('chronitem'):
                try:
                    if 'GIS' in chronItem.place.attrs:
                        # populate the record with the existing GIS data
                        self.logger.warning("Section not implemented")
                    else:
                        # try to resolve the location
                        locationName, coordinates = geocoder.geocode(chronItem.place.string)
                        # if we got data back
                        if locationName and coordinates:
                            location = {}
                            # location['xyz'] = ['abc','123','456']
                            location['date']  = self._cleanText(chronItem.date.string)
                            location['event'] = self._cleanText(chronItem.event.string)
                            location['place'] = self._cleanText(chronItem.place.string)
                            location['address'] = self._cleanText(locationName)
                            location['coordinates'] = [coordinates[0], coordinates[1]]
                            record['locations'].append(location)
                except Exception:
                    self.logger.warning("Could not resolve location record for " + filename)
            # write output record
            outfile = open(output + os.sep + yamlFilename, 'w')
            yaml.dump(record,outfile)
            outfile.close()
            self.logger.info("Wrote inferred location information to " + filename)

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
        #alchemy_api_key = params.get("infer","alchemy_api_key")
        google_api_key = params.get("infer","google_api_key")
        # infer location
        geocoder = geocoders.Google(domain='maps.google.com.au')
        self.inferLocations(source,output,report,geocoder,google_api_key)
        # infer entities
        # self.inferEntities(source,output,report,alchemy_api_key)
    