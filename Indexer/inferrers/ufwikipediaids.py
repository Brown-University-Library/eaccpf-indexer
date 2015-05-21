from Inferrer import Inferrer
from lxml import etree
import requests
import urllib

class ufWikipediaIDs_Inferrer(Inferrer):
    def __init__(self):
        self.cachedata = None
        self.dbptempl = u'http://fragments.dbpedia.org/2014/en?subject=dbpedia:{}&predicate=dbpedia-owl:wikiPageID'
        self.dbpheaders = {'Accept':"application/ld+json"}
        
        self.wdttempl = 'http://wikidata.dbpedia.org/sparql?default-graph-uri=http%3A%2F%2Fwikidata.dbpedia.org&query={}&format=application/json&timeout=30000'
        self.wdtquery = 'SELECT ?pid WHERE {{ <{}> dbpedia-owl:wikiPageID ?pid }}'
        
        
    def infer(self, doc, sleep):
        xml = doc.xml
        id = xml.findtext('.//{urn:isbn:1-931666-33-4}recordId')
        sources = xml.findall(".//{*}control/{*}sources/{*}source")
        
        wids = []
        urls = []
        depict=[]
        for source in sources: 
            href = source.get('{http://www.w3.org/1999/xlink}href')
            
            if href.startswith('http://wikidata.dbpedia.org/resource/'):
                sleep.append(True)
                
                urltempl = 'http://wikidata.dbpedia.org/sparql?default-graph-uri=http://wikidata.dbpedia.org&query=DESCRIBE+%3C{}%3E&format=application/json'
                rsurl = 'http://wikidata.dbpedia.org/resource/Q310694'
                url = urltempl.format(rsurl)
                
                data = requests.get(url)
                data = data.json()
                
                for k, v in data.items():
                	if k == rsurl:
                	    if 'http://www.w3.org/2000/01/rdf-schema#seeAlso' in v:
                	        for sa in v['http://www.w3.org/2000/01/rdf-schema#seeAlso']:
                	            urls.append( sa['value'] )
                	    
                	    if 'http://xmlns.com/foaf/0.1/depiction' in v:
                	        for sa in v['http://xmlns.com/foaf/0.1/depiction']:
                	            depict.append( sa['value'] )
                	    
                	    if 'http://www.w3.org/2002/07/owl#sameAs' in v:
                	        for sa in v['http://www.w3.org/2002/07/owl#sameAs']:
                	            if sa['value'].startswith('http://dbpedia.org/resource'):
                	                href = sa['value']
                	    
            
            if href.startswith('http://dbpedia.org/page/'):
                sleep.append(True)
                dbname = href.replace('http://dbpedia.org/page/', '')
                url = self.dbptempl.format(dbname)
                try:
                    resp = requests.get(url, headers=self.dbpheaders)
                    wid = resp.json()['@graph'][0]['dbpedia-owl:wikiPageID']
                    if wid:
                        wids.append(int(wid))
                except Exception as e:
                    pass
                    
            #http://wikidata.dbpedia.org/sparql?default-graph-uri=http://wikidata.dbpedia.org&query=DESCRIBE+%3Chttp://wikidata.dbpedia.org/resource/Q310694%3E&format=application/json
       
        outp = {}
       
        if wids:
            outp['wiki_id'] = wids 
        if urls:
            outp['inferred_url'] = urls
        if depict:
            outp['inferred_depiction'] = depict
        
        return outp if outp else None
            
    def append(self, inferred, xml):
        root = xml.getroot()
        doc = root.getchildren()[0]
        
        #Legacy workaround. TODO: Remove.
        if 'wids' in inferred:
            wikiIds = inferred['wids']
        elif 'wiki_id' in inferred:
            wikiIds = inferred['wiki_id']
        else:
            return
        
        for wid in wikiIds:
            newadd = etree.Element('field', name='wiki_id')
            newadd.text = str(wid)
            doc.append(newadd)