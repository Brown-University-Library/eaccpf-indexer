"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

# from AlchemyAPI import AlchemyAPI
from EacCpf import EacCpf

import Cfg
import Timer
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

    def __init__(self, actions, source, output, sleep=1.0, update=False):
        self.hashIndex = {}
        self.logger = logging.getLogger()
        # set parameters
        self.actions = actions
        self.output = output
        self.sleep = sleep
        self.source = source
        self.update = update
        
        self.ufs = []
        uflist = [ uf for uf in self.actions if uf.startswith('uf') ]
        for uf in uflist:
            ufmod = uf.lower()
            ufclass = "{}_Inferrer".format(uf)
            ufm = __import__('inferrers.{}'.format(ufmod), globals(), locals(), [ufclass])
            self.ufs.append(getattr(ufm, ufclass)())

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
        for filename in [f for f in os.listdir(self.source) if f.endswith(".xml")]:
            self.needsleep = []
            try:
                # record the name of the file so that we know we've processed it
                records.append(filename)
                doc = EacCpf(self.source + os.sep + filename)
                file_hash = doc.getHash()
                # if the file has not changed since the last run then skip it
                if self.update and filename in self.hashIndex and self.hashIndex[filename] == file_hash:
                    self.logger.info("No change since last update {0}".format(filename))
                    continue
                # process the file
                self.hashIndex[filename] = file_hash
                # load the inferred data file if it already exists
                inferred_data_filename = Utils.getFilenameWithAlternateExtension(filename,'yml')
                inferred = Utils.tryReadYaml(self.output, inferred_data_filename)
                freeText = doc.getFreeText()
                if 'locations' in self.actions:
                    places = doc.getLocations()
                    locations = self.inferLocations(places, sleep=self.sleep)
                    inferred['locations'] = locations                    
                if 'entities' in self.actions:
                    entities = self.inferEntitiesWithCalais(freeText)
                    inferred['entities'] = entities
                if 'named-entities' in self.actions:
                    namedEntities = self.inferEntitiesWithAlchemy(freeText)
                    inferred['named-entities'] = namedEntities
                if 'text-analysis' in self.actions:
                    textAnalysis = self.inferEntitiesWithNLTK(freeText)
                    inferred['text-analysis'] = textAnalysis
                    
                for uf in self.ufs:
                    ufdat = uf.infer(doc.xml, self.needsleep)
                    if ufdat:
                        inferred[type(uf).__name__] = ufdat
                # write inferred data to output file
                Utils.writeYaml(self.output, inferred_data_filename, inferred)
                self.logger.info("Wrote inferred data to {0}".format(inferred_data_filename))
                # sleep between requests
                if self.needsleep: 
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
        self.needsleep.append(True)
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
        
        TODO: This should probably cache responses from the geolocator, to avoid duplicate requests.
        TODO: Choose the geolocator based on config options.
        """
        #from geopy.geocoders.bing import Bing
        #from geopy.geocoders.googlev3 import GoogleV3
        #from geopy.geocoders.mapquest import MapQuest
        from geopy.geocoders.osm import Nominatim
        
        geolocator = Nominatim(country_bias='us', timeout=timeout, scheme='http', domain='open.mapquestapi.com/nominatim/v1')
        locations = []
        for place in places:
            
            if 'placeentry' in place:
                self.needsleep.append(True)
                try:
                    loc = geolocator.geocode(place['placeentry'], addressdetails=True)
                    address = loc.raw['address']
                    newaddr = {}
                    for x in address:
                        newaddr[Utils.cleanText(x)] = Utils.cleanText(address[x])
                    address = newaddr
                    location = place.copy()
                    location['address'] = address
                    location['coordinates'] = [loc.latitude, loc.longitude]
                    # split the address into parts
                    location['country'] = Utils.cleanText(address['country'])
                    
                    if 'region' in address:
                        location['region'] = Utils.cleanText(address['region'])
                    elif 'state' in address:
                        location['region'] = Utils.cleanText(address['state'])
                    
                    if 'city' in address:
                        location['city'] = Utils.cleanText(address['city'])
                    locations.append(location)
                    
                    time.sleep(sleep)
                except Exception as e:
                    self.logger.warning("Geocoding error", exc_info=True)
        return locations

    def run(self):
        """
        Execute analysis using the specified parameters.
        """
        with Timer.Timer() as t:
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
        # log execution time
        self.logger.info("Facter finished in {0}:{1}:{2}".format(t.hours, t.minutes, t.seconds))

def infer(params, update=False):
    """
    Execute processing actions with the specified parameters.
    """
    actions = params.get("infer", "actions").split(",")
    output = params.get("infer", "output")
    sleep = params.getfloat("infer", "sleep")
    source = params.get("infer", "input")
    facter = Facter(actions, source, output, sleep, update)
    facter.run()
