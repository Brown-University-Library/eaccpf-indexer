from .Inferrer import Inferrer
from lxml import etree
from xml.sax.saxutils import quoteattr

"""
    
"""
class ufHallHoagEAD_Inferrer(Inferrer):
    def __init__(self):
        self.cachedata = None
        self.ead = etree.parse('hallhoag.ead.xml')
        self.subjects = self._makeSubjectDict(self.ead)
        

    def _makeSubjectDict(self, ead):
        def f(x): return (x.text.find(' Call No. ') > -1)
        def subj(x): return x.text.split('   Call No. ')[0].strip()
        def callno(x): return x.text.split('   Call No. ')[1].strip()
        
        subjects = ead.findall("//{*}arrangement/{*}list/{*}item")
        subjects = list(filter(f, subjects))
        return dict(list(zip(list(map(callno, subjects)), list(map(subj, subjects)))))

    def infer(self, doc, sleep):
        xml = doc.xml
        media_type_dict = {
                            'PH': 'Photos',
                            'CL': 'Clippings',
                            'XX': 'Oversized',
                            'XXX': 'Oversized',
                            'AV': 'Audio/Visual Material',
                            'PC': 'Correspondence',
                            'IN': 'Index Cards',
                            'UM': 'Unidentified Material',
                            'Books': 'Books',
                          }
    
        id = xml.findtext('.//{urn:isbn:1-931666-33-4}recordId')
        localid = id.replace('US-RPB-', '')
        outp = {}
        c = self.ead.find(".//{{*}}c[@id='{}']".format(localid))
        
        if c==None:
            return {}
        
        outp['raw_ead_c'] = etree.tostring(c).decode()
        
        ext = c.findtext("{*}did//{*}extent")
        if ext: 
            outp['extent'] = ext.split(' ')[0]
        
        media_types = []
        p1 = c.find("{*}did/{*}container[@label='Part I']")
        conts = []
        if p1 != None: 
            if p1.text:
                for cont in p1.text.split(', '):
                    cont = cont.split(' ')[1]
                    conts.append(cont)
                    fcode = cont.split('-')[0]
                    if fcode in media_type_dict:
                        media_types.append(media_type_dict[fcode])
        
        outp['container'] = []
        outp['collection_parts'] = []
        
        if conts:
            outp['container_part1'] = list(set(conts))
            outp['container'] += list(set(conts))
            outp['collection_parts'].append('Part I')
            
        p2 = c.find("{*}did/{*}container[@label='Part II']")
        conts = []
        if p2 != None:
            if p2.text:
                for cont in p2.text.split(', '):
                    conts.append(cont)
                    fcode = cont.split('-')[0]
                    if fcode in media_type_dict:
                        media_types.append(media_type_dict[fcode])
    
        if conts:    
            outp['container_part2'] = conts
            outp['container'] += list(set(conts))
            outp['collection_parts'].append('Part II')
        
        if media_types:
            outp['media_type'] = list(set(media_types))
        
        subj = c.find('{*}controlaccess/{*}subject')
        
        if subj != None:
            outp['subject'] = subj.text.strip()
        
        cn = c.find("{*}controlaccess/{*}note/{*}p")
        
        if cn != None:
            outp['part1_call_number'] = cn.text
            
            if cn.text in self.subjects:
                outp['part1_category'] = self.subjects[cn.text]
        
        return outp