from Inferrer import Inferrer
from lxml import etree
import requests
import urllib

class ufWikipediaIDs_Inferrer(Inferrer):
    def __init__(self):
        self.dbptempl = u'http://fragments.dbpedia.org/2014/en?subject=dbpedia:{}&predicate=dbpedia-owl:wikiPageID'
        self.dbpheaders = {'Accept':"application/ld+json"}
        
        self.wdttempl = 'http://wikidata.dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fwikidata.dbpedia.org&query={}&format=application/json&timeout=30000'
        self.wdtquery = 'SELECT ?pid WHERE {{ <{}> dbpedia-owl:wikiPageID ?pid }}'
        
        
    def infer(self, xml, sleep):
        id = xml.findtext('.//{urn:isbn:1-931666-33-4}recordId')
        sources = xml.findall(".//{*}control/{*}sources/{*}source")
        
        wids = []
        for source in sources: 
            href = source.get('{http://www.w3.org/1999/xlink}href')
            if href.startswith('http://dbpedia.org/page/'):
                sleep.append(True)
                dbname = href.replace('http://dbpedia.org/page/', '')
                url = self.dbptempl.format(dbname)
                try:
                    resp = requests.get(url, headers=self.dbpheaders)
                    wid = resp.json()['@graph'][0]['dbpedia-owl:wikiPageID']
                    if wid:
                        wids.append(int(wid))
                except:
                    pass
            elif href.startswith('http://wikidata.dbpedia.org/resource/'):
                sleep.append(True)
                #dbname = href.replace('http://wikidata.dbpedia.org/resource/', '')
                dbname = href
                query = self.wdtquery.format(dbname)
                url = self.wdttempl.format(urllib.quote_plus(query))
                try:
                    resp = requests.get(url)
                    wid = resp.json()['results']['bindings'][0]['pid']['value']
                    if wid:
                        wids.append(int(wid))
                except:
                    pass
       
        if wids:
            return { 'wids'  : wids }
        else:
            return {}