"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

# from AlchemyAPI import AlchemyAPI
from EacCpf import EacCpf
# from geopy.geocoders.bing import Bing
from geopy.geocoders.googlev3 import GoogleV3
from geopy.geocoders.mapquest import MapQuest
from geopy.geocoders.osm import Nominatim

import Cfg
import Utils
import logging
import os
import time


class Facter(object):
    """
    Takes an EAC-CPF record, executes a semantic analysis of the contents and
    attempts to extract people, places, things, concepts from free text or 
    structured fields.
    """

    def __init__(self, actions, output, sleep, source, update=False):
        self.hashIndex = {}
        self.hashIndexFilename = ".index.yml"
        self.logger = logging.getLogger()
        # set parameters
        self.actions = actions
        self.output = output
        self.sleep = sleep
        self.source = source
        self.update = update

    def _addValueToDictionary(self, dic, key, value):
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
        address = str(Address)
        street = city = region = postal = country = ''
        try:
            # split the address string into segments
            segments = address.split(',')
            country = segments.pop().strip()
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
                    region = tokens.pop().strip()
                elif city == '':
                    city = ' '.join(tokens).strip()
            if segments and city == '':
                city = segments.pop().strip()
            # the remaining segments should be part of the street
            # address
            if segments:
                street = ','.join(segments).strip()
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
                entity['type'] = Utils.cleanText(e['_type'])
                entity['name'] = Utils.cleanText(e['name'])
                self._addValueToDictionary(out, "entities", entity)
        except:
            pass
        # relations
        try:
            for r in result.relations:
                relation = {}
                relation['type'] = Utils.cleanText(r['_type'])
                self._addValueToDictionary(out, "relations", relation)
        except:
            pass
        # topics
        try:
            for t in result.topics:
                top = {}
                top['categoryName'] = Utils.cleanText(t['categoryName'])
                self._addValueToDictionary(out, "topics", top)
        except:
            pass
        return out

    def infer(self):
        """
        Infer data for each source file.
        """
        # the list of records that have been processed
        records = []
        # process files
        files = os.listdir(self.source)
        for filename in files:
            if filename.endswith("xml"):
                try:
                    # record the name of the file so that we know we've processed it
                    records.append(filename)
                    doc = EacCpf(self.source + os.sep + filename)
                    fileHash = doc.getHash()
                    # if the file has not changed since the last run then skip it
                    if self.update and filename in self.hashIndex and self.hashIndex[filename] == fileHash:
                        self.logger.info("No change since last update {0}".format(filename))
                        continue
                    # process the file
                    self.hashIndex[filename] = fileHash
                    # load the inferred data file if it already exists
                    inferred_data_filename = Utils.getFilenameWithAlternateExtension(filename,'yml')
                    inferred = Utils.tryReadYaml(self.output, inferred_data_filename)
                    if 'locations' in self.actions:
                        places = doc.getLocations()
                        locations = self.inferLocations(places, sleep=self.sleep)
                        inferred['locations'] = locations
                    else:
                        freeText = doc.getFreeText()
                        if 'entities' in self.actions:
                            entities = self.inferEntitiesWithCalais(freeText)
                            inferred['entities'] = entities
                        if 'named-entities' in self.actions:
                            namedEntities = self.inferEntitiesWithAlchemy(freeText)
                            inferred['named-entities'] = namedEntities
                        if 'text-analysis' in self.actions:
                            textAnalysis = self.inferEntitiesWithNLTK(freeText)
                            inferred['text-analysis'] = textAnalysis
                    # write inferred data to output file
                    Utils.writeYaml(self.output, inferred_data_filename, inferred)
                    self.logger.info("Wrote inferred data to {0}".format(inferred_data_filename))
                    # sleep between requests
                    time.sleep(self.sleep)
                except:
                    self.logger.error("Inference failed {0}".format(filename), exc_info=Cfg.LOG_EXC_INFO)
        # return list of processed records
        return records

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
        # geolocator = Bing(api_key=self.geocoder_api_key)
        # geolocator = MapQuest(api_key=self.geocoder_api_key)
        # geolocator = Nominatim(country_bias='au')
        geolocator = GoogleV3()
        locations = []
        for place in places:
            # if there is an existing GIS attribute attached to the record then
            # don't process it
            if 'longitude' in place and 'latitude' in place:
                locations.append(place)
                self.logger.debug("Record has existing location data")
            elif 'placeentry' in place:
                # ISSUE #5 the geocoder can return multiple locations when an address is
                # not specific enough. Here we record each returned address, with the intent
                # that an archivist review the inferred data at a later date and then
                # manually select the appropriate address to retain for the record.
                try:
                    # for address, (lat, lng)  in geolocator.geocode(place['placeentry'], exactly_one=False, timeout=timeout):
                    for address, (lat, lng) in geolocator.geocode(place['placeentry'], exactly_one=False, region='au', timeout=timeout):
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
                        self.logger.debug("Found location {} {} {} {}".format(street, city, region, country))
                        time.sleep(sleep)
                except Exception as e:
                    self.logger.warning("Geocoding error", exc_info=True)
        return locations

    def run(self):
        """
        Execute analysis using the specified parameters.
        """
        # clear output folder
        if not os.path.exists(self.output):
            os.makedirs(self.output)
        if not self.update:
            Utils.cleanOutputFolder(self.output)
        # exit if there are no actions to execute
        if len(self.actions) < 1:
            return
        # load api keys, services for specified operations
        if 'named-entities' in self.actions:
            # configure alchemy
            pass
        if 'entities' in self.actions:
            try:
                from pythoncalais import Calais
                self.calais = Calais.Calais(self.calais_api_key, submitter="University of Melbourne, eScholarship Research Centre")
                self.calais.user_directives["allowDistribution"] = "false"
            except:
                self.calais_api_key = ''
                self.calais = None
        # check state before running
        assert os.path.exists(self.source), self.logger.error("Input path does not exist: {0}".format(self.source))
        assert os.path.exists(self.output), self.logger.error("Output path does not exist: {0}".format(self.output))
        # create an index of file hashes, so that we can track what has changed
        if self.update:
            self.hashIndex = Utils.loadFileHashIndex(self.output)
        # execute inference actions
        records = self.infer()
        # remove records from the index that were deleted in the source
        if self.update:
            self.logger.info("Clearing orphaned records from the file hash index")
            Utils.purgeIndex(records, self.hashIndex)
        # remove files from the output folder that are not in the index
        if self.update:
            self.logger.info("Clearing orphaned files from the output folder")
            Utils.purgeFolder(self.output, self.hashIndex)
        # write the updated file hash index
        Utils.writeFileHashIndex(self.hashIndex, self.output)

def infer(params, update=False):
    """
    Execute processing actions with the specified parameters.
    """
    actions = params.get("infer", "actions").split(",")
    output = params.get("infer", "output")
    sleep = params.getfloat("infer", "sleep")
    source = params.get("infer", "input")
    facter = Facter(actions, output, sleep, source, update)
    facter.run()
