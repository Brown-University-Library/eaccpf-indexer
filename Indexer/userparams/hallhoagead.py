from lxml import etree
from xml.sax.saxutils import quoteattr

"""
    This user ParamMaker reads an EAD file and provides parameters relevant to the current EAC document.
    
    It was created for indexing the Hall-Hoag collection of dissenting and extremist printed propaganda at the
    Brown University Library (http://library.brown.edu/collatoz/info.php?id=62), but may be useful as an example.
    
    User parameter generator classes must have names ending with _ParamMaker. The params() function is required; 
    it will receive one argument--the current EAC document--and must return a dictionary of strings ready for use
    as parameters in your XSLT stylesheet.
"""
class HallHoagEAD_ParamMaker(object):
    def __init__(self):
        print "Initializing HallHoagEAD_ParamMaker"
        self.ead = etree.parse('hallhoag.ead.xml')
        self.subjects = self._makeSubjectDict(self.ead)
        

    def _makeSubjectDict(self, ead):
        def f(x): return (x.text.find(' Call No. ') > -1)
        def subj(x): return x.text.split('   Call No. ')[0].strip()
        def callno(x): return x.text.split('   Call No. ')[1].strip()
        
        subjects = ead.findall("//{*}arrangement/{*}list/{*}item")
        subjects = filter(f, subjects)
        return dict(zip(map(callno, subjects), map(subj, subjects)))

    def params(self, xml):
        id = xml.findtext('//{urn:isbn:1-931666-33-4}recordId')
        localid = id.replace('US-RPB-', '')
        outp = {}
        c = self.ead.find(".//{{*}}c[@id='{}']".format(localid))
        
        if c==None:
            return {}
        
        outp['raw_ead_c'] = quoteattr(etree.tostring(c))
        
        p1 = c.find("{*}did/{*}container[@label='PartI']")
        outp['container_part1'] = quoteattr(p1.text if p1 != None else '')
        p2 = c.find("{*}did/{*}container[@label='PartII']")
        outp['container_part2'] = quoteattr(p2.text if p2 != None else '')
        
        subj = c.find('{*}controlaccess/{*}subject')
        outp['subject'] = quoteattr(subj.text if subj != None else '')
        
        cn = c.find("{*}controlaccess/{*}note/{*}p")
        
        if cn != None:
            outp['callno'] = quoteattr(cn.text)
            outp['category'] = quoteattr(self.subjects[cn.text])
        else:
            outp['callno'] = "''"   
            outp['category'] = "''"
        
        return outp