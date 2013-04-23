'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

from AlchemyAPI import AlchemyAPI
from BeautifulSoup import BeautifulSoup as soup
from pythoncalais import Calais
from geopy import * 
import logging
import os
import time
import yaml 

class Facter(object):
    '''
    Takes an EACCPF record, executes a semantic analysis of the contents and 
    attempts to extract people, places, things, concepts from free text or 
    structured fields.
    '''

    def __init__(self):
        '''
        Initialize class
        '''
        self.logger = logging.getLogger('feeder')

    def _addValueToDictionary(self,dic,key,value):
        '''
        For dictionaries that hold multiple values for each key.
        '''
        if not dic.has_key(key):
            dic[key] = []
        items = dic[key]
        items.append(value)

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
        if val == None:
            return ''
        clean = str(val)
        clean = clean.strip()
        # clean = clean.replace('\n','')
        return clean
    
    def _fixDate(self, date):
        '''
        Fix date string to make it conform to ISO standard.
        '''
        if 'T00:00:00Z' in date:
            return date
        return date + "T00:00:00Z"
    
    def _getAddressParts(self, Address):
        '''
        Parse a location record or address string into components.
        '''
        # defaults
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
        '''
        Get Calais result as a dictionary.
        '''
        out = {}
        # entities
        try:
            for e in result.entities:
                entity = {}
                #entity['typeReference'] = self._cleanText(e['_typeReference'])
                entity['type'] = self._cleanText(e['_type'])
                entity['name'] = self._cleanText(e['name'])
                self._addValueToDictionary(out, "entities", entity)
        except:
            pass
        # relations
        try:
            for r in result.relations:
                relation = {}
                #relation['typeReference'] = self._cleanText(r['_typeReference'])
                relation['type'] = self._cleanText(r['_type'])
                self._addValueToDictionary(out, "relations", relation)
        except:
            pass
        # topics
        try:
            for t in result.topics:
                top = {}
                #top['category'] = self._cleanText(t['category'])
                top['categoryName'] = self._cleanText(t['categoryName'])
                self._addValueToDictionary(out, "topics", top)
        except:
            pass
        return out
    
    def _getFreeTextFields(self, xml):
        '''
        Get content from free text fields.
        '''
        freetext = ''
        # /eac-cpf/identity/nameEntry/part
        nameentry = xml.find('nameentry')
        if nameentry:
            parts = nameentry.findAll('part')
            if parts:
                for p in parts:
                    freetext += self._cleanText(p.getString())
        # /eac-cpf/description/biogHist/abstract
        # /eac-cpf/description/biogHist/p
        bioghist = xml.find('bioghist')
        if bioghist:
            abstract = bioghist.find('abstract')
            if abstract:
                freetext += self._cleanText(abstract.getText())
            ps = bioghist.findAll('p')
            if ps:
                for p in ps:
                    freetext += self._cleanText(p.getString())
        # /eac-cpf/description/function/descNote/p
        function = xml.find('function')
        if function:
            functions = function.findAll('p')
            if functions:
                for f in functions:
                    freetext += self._cleanText(f.getString())
        # return
        return freetext

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
            return {'comment':'Inferred entity and location data extracted from ' + filename}
        
    def _getYamlFilename(self, filename):
        '''
        Takes a file name and returns a name with .yml appended.
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
            
    def _mergeResultWithRecord(self, record, result):
        '''
        Merge the result dictionary with the record dictionary.
        '''
        for key in result.keys():
            record[key] = result[key]
        return record
    
    def _setDateField(self, target, fieldname, source):
        '''
        Try to set the named field with the specified date string.
        '''
        try:
            if source is not None:
                if hasattr(source,'standarddate'):
                    date = self._cleanText(source['standarddate'])
                    target[fieldname] = self._fixDate(date)
        except:
            pass
    
    def _setStringField(self, target, fieldname, source):
        '''
        Try to set the named field with the specified source object.
        '''
        try:
            if source is not None:
                target[fieldname] = self._cleanText(source.string)
        except:
            pass
    
    def inferEntitiesWithAlchemy(self, source, output, api_key, sleep=0., report=None):
        '''
        For each input file, attempt to extract people, things, concepts and 
        place names from free text fields. Sleep for the specified number of 
        seconds between requests.
        '''
        # check state
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
        # Create an AlchemyAPI object, load API key
        alchemy = AlchemyAPI.AlchemyAPI() 
        alchemy.setAPIKey(api_key)

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
            # clear the existing entities section before populating
            record['inferred_alchemy'] = []
            # get the free text fields from the record
            freetext = self._getFreeTextFields(xml)
            # extract a ranked list of named entities
            result = alchemy.TextGetRankedNamedEntities(freetext);
            self.logger.info(result)
            # record['entities'] = result
            # write output record
            outfile = open(output + os.sep + yamlFilename, 'w')
            yaml.dump(record,outfile)
            outfile.close()
            self.logger.info("Wrote inferred entities to " + yamlFilename)
            # sleep between requests
            time.sleep(sleep)
        
    def inferEntitiesWithCalais(self, source, output, api_key, sleep=0., report=None):
        # create an OpenCalais object, load API key
        calais = Calais.Calais(api_key, submitter="University of Melbourne, eScholarship Research Centre")
        calais.user_directives["allowDistribution"] = "false"
        # check state
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
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
            # clear the existing entities section before populating
            # get free text fields from the record
            freetext = self._getFreeTextFields(xml)
            try:
                # extract entities
                calais_result = calais.analyze(freetext)
                # merge the existing record with the new results
                result = self._getCalaisResultAsDictionary(calais_result)
                record = self._mergeResultWithRecord(record, result)
                # write output record
                outfile = open(output + os.sep + yamlFilename, 'w')
                yaml.dump(record,outfile)
                outfile.close()
                self.logger.info("Wrote inferred entities to " + yamlFilename)
            except Exception:
                self.logger.warning("Could not complete inference operation for " + filename, exc_info=True)
            # sleep between requests
            time.sleep(sleep)
    
    def inferEntitiesWithNLTK(self, source, output, report=None):
        '''
        Infer entities from free text using Natural Language Toolkit.
        Attempt to identify people and things.
        '''
        # create output folder
        self._makeCache(output)
        # check state
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        if report:
            assert os.path.exists(report), self.logger.warning("Report path does not exist: " + report)
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
            # clear the existing entities section before populating
            record['inferred_nltk'] = []
            # get the free text fields from the record
            freetext = self._getFreeTextFields(xml)
            self.logger.info(freetext)
            # infer entities
            # write output record
            outfile = open(output + os.sep + yamlFilename, 'w')
            yaml.dump(record,outfile)
            outfile.close()
            self.logger.info("Wrote inferred entities to " + yamlFilename)
        
    def inferLocations(self, source, output, geocoder, sleep=0., report=None):
        '''
        For each EAC-CPF input file, extract the address from each cronitem and
        attempt to resolve its geographic coordinates. Sleep for the specified 
        number of seconds between requests.
        @see https://github.com/geopy/geopy/blob/master/docs/google_v3_upgrade.md.
        '''
        # check state
        assert os.path.exists(source), self.logger.warning("Specified path does not exist: " + source)
        # process files
        files = os.listdir(source)
        for filename in files:
            if filename.endswith(".xml"):
                try:
                    # read source data
                    infile = open(source + os.sep + filename,'r')
                    infile_data = infile.read()
                    infile.close()
                    xml = soup(infile_data)
                    # if the file already exists, load the current data
                    yamlFilename = self._getYamlFilename(filename)
                    inferred = self._getRecord(output,yamlFilename)
                    # clear the existing locations section before populating
                    inferred['locations'] = []
                    # for each chronitem
                    for item in xml.findAll('chronitem'):
                        try:
                            # build the place record
                            place = {}
                            self._setStringField(place,'place',item.find('placeentry'))
                            self._setStringField(place,'event',item.find('event'))
                            if item.find('fromdate') is not None:
                                self._setDateField(place,'eventFrom',item.find('fromdate','standarddate'))
                            if item.find('todate') is not None:
                                self._setDateField(place,'eventTo',item.find('todate','standarddate'))
                            # if there is an existing GIS attribute attached to the record, don't process it
                            if 'place' in place and place['place'] is not None:
                                if 'GIS' in place or 'gis' in place:
                                    inferred['locations'].append(place)
                                    self.logger.warning("Record has existing location data")
                                else:
                                    # ISSUE #5 the geocoder can return multiple locations when an address is
                                    # not specific enough. We create a record for each address, with the intent
                                    # that an archivist review the inferred data at a later date and then
                                    # manually select the appropriate address to retain for the record.
                                    for address, (lat, lng) in geocoder.geocode(place['place'],exactly_one=False,region='au'):
                                        location = place.copy()
                                        location['address'] = self._cleanText(address)
                                        location['coordinates'] = [lat, lng]
                                        # split the address into parts
                                        street, city, region, postal_code, country = self._getAddressParts(address)
                                        location['country'] = country
                                        location['postal_code'] = postal_code
                                        location['region'] = region
                                        location['city'] = city
                                        location['street'] = street
                                        # add the location record
                                        inferred['locations'].append(location)
                        except Exception:
                            self.logger.warning("Could not complete processing on place record in " + filename, exc_info=True)
                            continue
                    # write inferred data to file
                    outfile = open(output + os.sep + yamlFilename, 'w')
                    yaml.dump(inferred,outfile)
                    outfile.close()
                    self.logger.info("Wrote inferred locations to " + yamlFilename)
                    # sleep between requests
                    time.sleep(sleep)
                except Exception:
                    self.logger.warning("Could not resolve location for " + filename, exc_info=True)
                    continue

    def run(self, Params):
        '''
        Execute analysis using the specified parameters.
        '''
        # get parameters
        actions = Params.get("infer","actions").split(",")
        output = Params.get("infer","output")
        report = Params.get("infer","report")
        sleep = float(Params.get("infer","sleep"))
        source = Params.get("infer","input")
        # create output folder
        self._makeCache(output)
        # execute inferences for each selected type
        for action in actions:
            if 'location' in action:
                geocoder = geocoders.GoogleV3()
                self.inferLocations(source,output,geocoder,sleep,report)
            if 'entities' in action:
                # infer entities with Alchemy
                #alchemy_api_key = Params.get("infer","alchemy_api_key")
                #self.inferEntitiesWithAlchemy(source,output,alchemy_api_key,sleep,report)
                # infer entities with NLTK
                # self.inferEntitiesWithNLTK(source, output, report)
                # infer entities with Open Calais
                calais_api_key = Params.get("infer","calais_api_key")
                self.inferEntitiesWithCalais(source,output,calais_api_key,sleep,report)
        