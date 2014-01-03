"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from AlchemyAPI import AlchemyAPI
from EacCpf import EacCpf
from geopy.geocoders import *
import Utils
import logging
import os
import time

LOG_EXC_INFO = False


class Facter(object):
    """
    Takes an EAC-CPF record, executes a semantic analysis of the contents and
    attempts to extract people, places, things, concepts from free text or 
    structured fields.
    """

    def __init__(self):
        """
        Initialize class
        """
        self.hashIndexFilename = ".index.yml"
        self.logger = logging.getLogger()

    def _addValueToDictionary(self,dic,key,value):
        """
        For dictionaries that hold multiple values for each key.
        """
        if not dic.has_key(key):
            dic[key] = []
        items = dic[key]
        items.append(value)

    def _getAddressParts(self, Address):
        """
        Parse a location record or address string into components.
        """
        street = city = region = postal = country = ''
        try:
            # split the address string into segments
            segments = Address.split(',')
            country = segments.pop().strip().encode('utf8')
            # a token is a postal code if it has numbers in it
            tokens = segments.pop().strip().split(' ')
            for token in reversed(tokens):
                if any(c.isdigit() for c in token):
                    postal = token + ' ' + postal
                    tokens.pop()
            postal = str(postal.strip())
            # the next token should be the region and the remainder should
            # be the city
            for token in reversed(tokens):
                if region == '':
                    region = tokens.pop().strip().encode('utf8')
                elif city == '':
                    city = ' '.join(tokens).strip().encode('utf8')
            if segments and city == '':
                city = segments.pop().strip().encode('utf8')
            # the remaining segments should be part of the street
            # address
            if segments:
                street = ','.join(segments).strip().encode('utf8')
        except:
            pass
        return street, city, region, postal, country
    
    def _getCalaisResultAsDictionary(self, result):
        """
        Convert Calais result to dictionary structure.
        """
        out = {}
        # entities
        try:
            for e in result.entities:
                entity = {}
                #entity['typeReference'] = self._cleanText(e['_typeReference'])
                entity['type'] = Utils.cleanText(e['_type'])
                entity['name'] = Utils.cleanText(e['name'])
                self._addValueToDictionary(out, "entities", entity)
        except:
            pass
        # relations
        try:
            for r in result.relations:
                relation = {}
                #relation['typeReference'] = self._cleanText(r['_typeReference'])
                relation['type'] = Utils.cleanText(r['_type'])
                self._addValueToDictionary(out, "relations", relation)
        except:
            pass
        # topics
        try:
            for t in result.topics:
                top = {}
                #top['category'] = self._cleanText(t['category'])
                top['categoryName'] = Utils.cleanText(t['categoryName'])
                self._addValueToDictionary(out, "topics", top)
        except:
            pass
        return out

    def inferEntitiesWithAlchemy(self, Text):
        """
        For each input file, attempt to extract people, things, concepts and 
        place names from free text fields. Sleep for the specified number of 
        seconds between requests.
        """
        return {}

    def inferEntitiesWithCalais(self, Text):
        """
        Infer named entities from free text fields using OpenCalais web
        service.
        """
        calais_result = self.calais.analyze(Text)
        result = self._getCalaisResultAsDictionary(calais_result)
        return result

    def inferEntitiesWithNLTK(self, Text):
        """
        Infer entities from free text using Natural Language Toolkit.
        Attempt to identify people and things.
        """
        return {}

    def inferLocations(self, places, sleep=1.0, timeout=2.0):
        """
        For each EAC-CPF input file, extract the address from each cronitem and
        attempt to resolve its geographic coordinates. Sleep for the specified 
        number of seconds between requests.
        @see https://github.com/geopy/geopy/blob/master/docs/google_v3_upgrade.md.
        """
        # geolocator = GoogleV3()
        geolocator = Nominatim(country_bias='au')
        locations = []
        for place in places:
            # if there is an existing GIS attribute attached to the record then
            # don't process it
            if 'longitude' in place and 'latitude' in place:
                locations.append(place)
                self.logger.debug("Record has existing location data")
            else:
                # ISSUE #5 the geocoder can return multiple locations when an address is
                # not specific enough. Here we record each returned address, with the intent
                # that an archivist review the inferred data at a later date and then
                # manually select the appropriate address to retain for the record.
                try:
                    # for address, (lat, lng) in geolocator.geocode(place['placeentry'], exactly_one=False, region='au', timeout=sleep):
                    for address, (lat, lng) in geolocator.geocode(place['placeentry'], exactly_one=False, timeout=timeout):
                        location = place.copy()
                        location['address'] = Utils.cleanText(address)
                        location['coordinates'] = [lat, lng]
                        # split the address into parts
                        street, city, region, postal_code, country = self._getAddressParts(address)
                        location['country'] = country
                        location['postal_code'] = postal_code
                        location['region'] = region
                        location['city'] = city
                        location['street'] = street
                        locations.append(location)
                        self.logger.debug("Found location {0}, {1}, {2}".format(city, region, country))
                        time.sleep(sleep)
                except Exception as e:
                    self.logger.warning("Geocoding error", exc_info=True)
        return locations

    def infer(self, Source, Output, Actions, HashIndex, Sleep, Params, Update):
        """
        Infer data for each source file.
        """
        # the list of records that have been processed
        records = []
        # process files
        files = os.listdir(Source)
        for filename in files:
            if filename.endswith('.xml'):
                try:
                    # record the name of the file
                    records.append(filename)
                    doc = EacCpf(Source + os.sep + filename)
                    fileHash = doc.getHash()
                    # if the file has not changed since the last run then skip it
                    if Update:
                        if filename in HashIndex and HashIndex[filename] == fileHash:
                            self.logger.info("No change since last update " + filename)
                            continue
                    # process the file
                    HashIndex[filename] = fileHash
                    # load the inferred data file if it already exists
                    inferred_filename = Utils.getFilenameWithAlternateExtension(filename,'yml')
                    inferred = Utils.tryReadYaml(Output, inferred_filename)
                    freeText = doc.getFreeText()
                    if 'locations' in Actions:
                        places = doc.getLocations()
                        locations = self.inferLocations(places, sleep=Sleep)
                        inferred['locations'] = locations
                    if 'entities' in Actions:
                        entities = self.inferEntitiesWithCalais(freeText)
                        inferred['entities'] = entities
                    if 'named-entities' in Actions:
                        namedEntities = self.inferEntitiesWithAlchemy(freeText)
                        inferred['named-entities'] = namedEntities
                    if 'text-analysis' in Actions:
                        textAnalysis = self.inferEntitiesWithNLTK(freeText)
                        inferred['text-analysis'] = textAnalysis
                    # write inferred data to file
                    Utils.writeYaml(Output, inferred_filename, inferred)
                    self.logger.info("Wrote inferred data to " + inferred_filename)
                    # sleep between requests
                    time.sleep(Sleep)
                except:
                    self.logger.error("Inference failed {0}".format(filename), exc_info=LOG_EXC_INFO)
        # return list of processed records
        return records

    def run(self, Params, Update=False, StackTrace=False):
        """
        Execute analysis using the specified parameters.
        """
        # get parameters
        actions = Params.get("infer", "actions").split(",")
        output = Params.get("infer", "output")
        sleep = Params.getfloat("infer", "sleep")
        source = Params.get("infer", "input")
        # clear output folder
        if not os.path.exists(output):
            os.makedirs(output)
        if not Update:
            Utils.cleanOutputFolder(output)
        # exit if there are no actions to execute
        if len(actions) < 1:
            return
        # load api keys, services for specified operations
        if 'named-entities' in actions:
            try:
                self.alchemy_api_key = Params.get("infer", "alchemy_api_key")
            except:
                self.alchemy_api_key = ''
        if 'entities' in actions:
            try:
                self.calais_api_key = Params.get("infer", "calais_api_key")
                # create an OpenCalais object, load API key
                from pythoncalais import Calais
                self.calais = Calais.Calais(self.calais_api_key, submitter="University of Melbourne, eScholarship Research Centre")
                self.calais.user_directives["allowDistribution"] = "false"
            except:
                self.calais_api_key = ''
                self.calais = None
        # check state before running
        assert os.path.exists(source), self.logger.error("Input path does not exist: {0}".format(source))
        assert os.path.exists(output), self.logger.error("Output path does not exist: {0}".format(output))
        # create an index of file hashes, so that we can track what has changed
        hashIndex = {}
        if Update:
            hashIndex = Utils.loadFileHashIndex(output)
        # execute inference actions
        records = self.infer(source, output, actions, hashIndex, sleep, Params, Update)
        # remove records from the index that were deleted in the source
        if Update:
            self.logger.info("Clearing orphaned records from the file hash index")
            Utils.purgeIndex(records, hashIndex)
        # remove files from the output folder that are not in the index
        if Update:
            self.logger.info("Clearing orphaned files from the output folder")
            Utils.purgeFolder(output, hashIndex)
        # write the updated file hash index
        Utils.writeFileHashIndex(hashIndex, output)
