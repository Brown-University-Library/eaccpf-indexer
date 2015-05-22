from Inferrer import Inferrer
from lxml import etree
import requests
import urllib

class ufWikipediaIDs_Inferrer(Inferrer):
    def __init__(self):
        self.cachedata = None
        self.dbptempl = u'http://fragments.dbpedia.org/2014/en?subject=dbpedia:{}&predicate=dbpedia-owl:wikiPageID'
        self.dbpheaders = {'Accept':"application/json"}
        
        self.wdttempl = 'http://wikidata.dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fwikidata.dbpedia.org&query={}&format=application/json&timeout=30000'
        self.wdtquery = 'SELECT ?pid WHERE {{ <{}> dbpedia-owl:wikiPageID ?pid }}'
        
        
    def infer(self, doc, sleep):
        xml = doc.xml
        id = xml.findtext('.//{urn:isbn:1-931666-33-4}recordId')
        sources = xml.findall(".//{*}control/{*}sources/{*}source")
        
        wids = []
        urls = []
        depict=[]
        wikidata_id = False
        for source in sources: 
            href = source.get('{http://www.w3.org/1999/xlink}href')
            
            if href.startswith('http://wikidata.dbpedia.org/page/'):
                href = href.replace('http://wikidata.dbpedia.org/page/', 'http://wikidata.dbpedia.org/resource/')
            
            if href.startswith('http://wikidata.dbpedia.org/resource/'):
                sleep.append(True)
                
                urltempl = 'http://wikidata.dbpedia.org/sparql?default-graph-uri=http://wikidata.dbpedia.org&query=DESCRIBE+%3C{}%3E&format=application/json'
                wikidata_id = href.replace('http://wikidata.dbpedia.org/resource/', '')
                url = urltempl.format(href)
                
                data = requests.get(url)
                data = data.json()
                
                if href in data:
                    v = data[href]
            	    if 'http://www.w3.org/2000/01/rdf-schema#seeAlso' in v:
            	        for sa in v['http://www.w3.org/2000/01/rdf-schema#seeAlso']:
            	            urls.append( sa['value'] )
            	    
            	    if 'http://xmlns.com/foaf/0.1/depiction' in v:
            	        for sa in v['http://xmlns.com/foaf/0.1/depiction']:
            	            depict.append( sa['value'] )
            	    
            	    if 'http://www.w3.org/2002/07/owl#sameAs' in v:
            	        for sa in v['http://www.w3.org/2002/07/owl#sameAs']:
            	            if sa['value'].startswith('http://dbpedia.org/resource/'):
            	                href = sa['value'].replace('http://dbpedia.org/resource/', 'http://dbpedia.org/page/')
            
            if href.startswith('http://dbpedia.org/page/'):
                sleep.append(True)
                url = href.replace('http://dbpedia.org/page/', 'http://dbpedia.org/data/')+'.json'
                resname = href.replace('http://dbpedia.org/page/', 'http://dbpedia.org/resource/')
                try:
                    resp = requests.get(url, headers=self.dbpheaders)
                    data = resp.json()[resname]
                    if "http://dbpedia.org/ontology/wikiPageExternalLink" in data:
                        for url in data["http://dbpedia.org/ontology/wikiPageExternalLink"]:
                            urls.append(url['value'])
                    if (not wikidata_id) and ("http://www.w3.org/2002/07/owl#sameAs" in data):
                        for i in data["http://www.w3.org/2002/07/owl#sameAs"]:
                            if i['value'].startswith('http://wikidata.dbpedia.org/resource/'):
                                wikidata_id = i['value'].replace('http://wikidata.dbpedia.org/resource/', '')
                    if "http://xmlns.com/foaf/0.1/depiction" in data:
                        for i in data["http://xmlns.com/foaf/0.1/depiction"]:
                            depict.append(i['value'])
                    if "http://dbpedia.org/ontology/wikiPageID" in data:
                        for i in data["http://dbpedia.org/ontology/wikiPageID"]:
                            wids.append(i['value'])
                    
                except Exception as e:
                    pass
                    
            #http://wikidata.dbpedia.org/sparql?default-graph-uri=http://wikidata.dbpedia.org&query=DESCRIBE+%3Chttp://wikidata.dbpedia.org/resource/Q310694%3E&format=application/json
       
        #TODO: Pull each URL, discard 404s, record titles.
       
        outp = {}
       
        if wids:
            outp['wiki_id'] = list(set(wids))
        if urls:
            outp['inferred_url'] = list(set(urls))
        if depict:
            outp['inferred_depiction'] = list(set(depict))
        if wikidata_id:
            outp['wikidata_id'] = str(wikidata_id)
        
        return outp