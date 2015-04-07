from lxml import etree
import requests
import json
from datetime import date
from xml.sax.saxutils import quoteattr

class WikipediaIDs_ParamMaker(object):
    def __init__(self):
        self.urltempl = 'http://fragments.dbpedia.org/2014/en?subject=dbpedia:{}&predicate=dbpedia-owl:wikiPageID'
        self.dbpheaders = {'Accept':"application/ld+json"}
        
    def params(self, xml):
        id = xml.findtext('//{urn:isbn:1-931666-33-4}recordId')
        sources = xml.findall("//{*}control/{*}sources/{*}source")
        dbname = ''
                
        for source in sources: 
            href = source.get('{http://www.w3.org/1999/xlink}href')
            if href.startswith('http://dbpedia.org/page/'):
                dbname = href.replace('http://dbpedia.org/page/', '')
                break
        
        if '' == dbname:
            return {}
        
        url = self.urltempl.format(dbname)
        
        try:
            resp = requests.get(url, headers=self.dbpheaders)
            wid = resp.json()['@graph'][0]['dbpedia-owl:wikiPageID']
            
            if wid:
                return {'wikipedia-id': '"{}"'.format(wid)}
            else:
                return {'wikipedia-id': '""'}
        except: 
            return {'wikipedia-id': '""'}