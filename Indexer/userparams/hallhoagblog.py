#No longer in use; now pulled dynamically via a php script.

from lxml import etree
from datetime import date
from xml.sax.saxutils import quoteattr
import json

class HallHoagBlog_ParamMaker(object):
    def __init__(self):
        print "Initializing HallHoagBlog_ParamMaker"
        self.postlinks = {}
        yr = 2013
        mt = 1
        cdate = date(yr, mt, 1)
        while cdate <= date.today():
            url = "http://blogs.brown.edu/hallhoag/{}/{:02}/feed/".format(yr, mt)
            rss = etree.parse(url)
            items = rss.findall("//channel/item")
            ctitle = rss.findtext("//channel/title")
            
            for i in items:  
                id = self._findId(i)
                
                if id:
                    id = "US-RPB-{}".format(id)
                    
                    if id not in self.postlinks:
                        self.postlinks[id] = []
                    
                    title = i.findtext("title") + " | " + ctitle
                    self.postlinks[id].append({
                                        'link': i.findtext('link'),
                                        'title': title,
                                        'abstract': i.findtext('description'),
                                     })
            
            mt += 1
            if mt > 12:
                mt = 1
                yr += 1
            cdate = date(yr, mt, 1)
        
    def _findId(self, xml):
        for cat in xml.findall('category'): 
            if cat.text.startswith('HH_'):
                return cat.text
        
        return False
        
    def params(self, xml):
        id = xml.findtext('//{urn:isbn:1-931666-33-4}recordId')
        if id in self.postlinks:
            return {'blogdata': "'"+json.dumps(self.postlinks[id])+"'"}
        else:
            return {'blogdata': "'"+json.dumps([])+"'"}