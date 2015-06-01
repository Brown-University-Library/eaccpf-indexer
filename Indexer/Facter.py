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

    def __init__(self, actions, source, output, sleep=1.0, update=False, cachedir=None):
        self.hashIndex = {}
        self.logger = logging.getLogger()
        # set parameters
        self.actions = actions
        self.output = output
        self.sleep = sleep
        self.source = source
        self.update = update
        self.cachedir = cachedir
        self.locationCache = {}
        
        if cachedir:
            self.locationCache = Utils.tryReadYaml(self.cachedir, '.location_cache.yml')
        
        """
        #Workaround for "New York, United States"--Nominatim assumes I mean the city.
        nys = {u'display_name': u'New York, United States of America', u'importance': 0.77784291474703, u'place_id': u'151141023', 
                u'lon': u'-75.8449946', u'lat': u'43.1561681', u'osm_type': u'relation', 
                u'licence': u'Data \xa9 OpenStreetMap contributors, ODbL 1.0. http://www.openstreetmap.org/copyright', 
                u'osm_id': u'61320', u'boundingbox': [u'40.477399', u'45.0158611', u'-79.7623534', u'-71.7897328'], 
                u'type': u'administrative', u'class': u'boundary', 
                u'address': {u'country': u'United States of America', u'state': u'New York', u'country_code': u'us'}, 
                u'icon': u'http://mq-open-search-ext-lm05.ihost.aol.com:8000/nominatim/v1/images/mapicons/poi_boundary_administrative.p.20.png'}
        self.locationCache['New York, United States'] = nys
        """
        
        self.ufs = []
        uflist = [ uf for uf in self.actions if uf.startswith('uf') ]
        for uf in uflist:
            ufmod = uf.lower()
            ufclass = "{}_Inferrer".format(uf)
            ufm = __import__('inferrers.{}'.format(ufmod), globals(), locals(), [ufclass])
            newuf = getattr(ufm, ufclass)()
            newuf.cache = Utils.tryReadYaml(self.cachedir, "{}_cache".format(ufclass))
            self.ufs.append(newuf)

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
        
        #set up actions.
        actions = {}
        if 'locations' in self.actions:
            actions['locations'] = self.inferLocations
        if 'entities' in self.actions:
            actions['entities'] =self.inferEntitiesWithCalais
        if 'named-entities' in self.actions:
            actions['named-entities'] = self.inferEntitiesWithAlchemy
        if 'text-analysis' in self.actions:
            actions['text-analysis'] = self.inferEntitiesWithNLTK
        for uf in self.ufs:
            actions[type(uf).__name__] = uf.infer
            
        
        for filename in [f for f in os.listdir(self.source) if f.endswith(".xml")]:
            self.needsleep = []
            records.append(filename)
            
            doAll = True
            
            doc = EacCpf(self.source + os.sep + filename)
            # if the file has not changed don't redo successful inferences.
            file_hash = doc.getHash()
            if self.update and filename in self.hashIndex and self.hashIndex[filename] == file_hash:
                self.logger.info("No change since last update {0}".format(filename))
                doAll = False
            
            self.hashIndex[filename] = file_hash
            
            # load the inferred data file if it already exists
            inferred_data_filename = Utils.getFilenameWithAlternateExtension(filename,'yml')
            inferred = Utils.tryReadYaml(self.output, inferred_data_filename)
            
            for actname, action in actions.items():
                if doAll or (actname not in inferred):
                    try:
                        inferred[actname] = action(doc, self.needsleep)
                    except Exception as e:
                        self.logger.error("Inference action {0} failed for file {1}. Exception: {2}".format(actname, filename, str(e)), exc_info=Cfg.LOG_EXC_INFO)
                    
            
            Utils.writeYaml(self.output, inferred_data_filename, inferred)
            self.logger.info("Wrote inferred data to {0}".format(inferred_data_filename))
            
            # Sleep between requests if needed.
            if self.needsleep: 
                time.sleep(self.sleep)
        # return list of processed records
        return records

    def inferEntitiesWithAlchemy(self, doc, sleep):
        """
        For each input file, attempt to extract people, things, concepts and 
        place names from free text fields. Sleep for the specified number of 
        seconds between requests.
        """
        Text = doc.getFreeText()
        return {}

    def inferEntitiesWithCalais(self, doc, sleep):
        """
        Infer named entities from free text fields using OpenCalais web
        service.
        """
        sleep.append(True)
        Text = doc.getFreeText()
        calais_result = self.calais.analyze(Text)
        result = self._getCalaisResultAsDictionary(calais_result)
        return result

    def inferEntitiesWithNLTK(self, doc, sleep):
        """
        Infer entities from free text using Natural Language Toolkit.
        Attempt to identify people and things.
        """
        Text = doc.getFreeText()
        return {}

    def inferLocations(self, doc, sleep, sleeptime=False, timeout=2.0):
        """
        For each EAC-CPF input file, extract the address from each cronitem and
        attempt to resolve its geographic coordinates. Sleep for the specified 
        number of seconds between requests.
        
        TODO: Choose the geolocator based on config options.
        """
        #from geopy.geocoders.bing import Bing
        #from geopy.geocoders.googlev3 import GoogleV3
        #from geopy.geocoders.mapquest import MapQuest
        if not sleeptime:
            sleeptime = self.sleep
        
        from geopy.geocoders.osm import Nominatim
        
        geolocator = Nominatim(timeout=timeout, scheme='http', domain='open.mapquestapi.com/nominatim/v1')
        locations = []
        first = True
        places = doc.getLocations()
        
        for place in places:
            if 'placeentry' in place:
                if place['placeentry'] not in self.locationCache:
                    sleep.append(True)
                    if not first:
                        time.sleep(sleeptime)
                    loc = geolocator.geocode(place['placeentry'], addressdetails=True, language="en")
                    
                    if loc:
                        self.locationCache[place['placeentry']] = loc.raw
                    else: 
                        raise Exception("Geolocation error (location: '{0}')".format(place['placeentry']))
                    first = False
                
                loc = self.locationCache[place['placeentry']]
                
                address = loc['address']
                newaddr = {}
                for x in address:
                    newaddr[Utils.cleanText(x)] = Utils.cleanText(address[x])
                address = newaddr
                location = place.copy()
                location['address'] = address
                location['coordinates'] = [float(loc['lat']), float(loc['lon'])]
                # split the address into parts
                location['country'] = address['country'].strip()
                
                if 'region' in address:
                    location['region'] = address['region'].strip()
                elif 'state' in address:
                    location['region'] = address['state'].strip()
                
                if 'city' in address:
                    location['city'] = address['city'].strip()
                
                locations.append(location)
                    
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
            if self.update:
                # remove records from the index that were deleted in the source
                self.logger.info("Clearing orphaned records from the file hash index")
                Utils.purgeIndex(records, self.hashIndex)

                # remove files from the output folder that are not in the index
                self.logger.info("Clearing orphaned files from the output folder")
                #Utils.purgeFolder(self.output, self.hashIndex)

            # write the updated file hash index
            Utils.writeFileHashIndex(self.hashIndex, self.output)
            
            #Write the location cache.
            Utils.writeYaml(self.cachedir, '.location_cache.yml', self.locationCache)
            
            for uf in self.ufs:
                if uf.cache:
                    Utils.writeYaml(self.cachedir, "{}_cache".format(type(uf).__name__), uf.cache)
            
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
    cachedir = params.get("infer", "cachedir")
    facter = Facter(actions, source, output, sleep, update, cachedir)
    facter.run()
