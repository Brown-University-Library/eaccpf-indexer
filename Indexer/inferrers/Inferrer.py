from lxml import etree
import yaml

class Inferrer(object):
    """
        This is an abstract class. Inferrers' class names must begin with 'uf' and end with '_Inferrer'
    """
    def __init__(self):
        self.cachedata = None
    
    def infer(self, doc, sleep):
        """
            The infer method should return a dictionary of content that will be 
            converted to YAML and saved in the inferred data file for the XML document xml.
            
            If infer() does anything that should cause the Facter script to sleep temporarily,
            infer should append True to sleep.
            
            The xml for the document is in doc.xml.
        """
        pass
    
    def append(self, inferred, xml):
        """
            `inferred` is the dictionary saved from infer. Insert this data into xml. Return values are ignored.
            
            This method just creates a new node for each item in the dictionary. It's probably
            what you want in most cases.
        """
        root = xml.getroot()
        doc = root.getchildren()[0]
        for k,v in inferred.items():
            if v:
                if type(v).__name__ in ['unicode', 'str']:
                    newadd = etree.Element('field', name=k)
                    newadd.text = v
                    doc.append(newadd)
                elif type(v).__name__ in ['int', 'float']:
                    newadd = etree.Element('field', name=k)
                    newadd.text = str(v)
                    doc.append(newadd)
                else:
                    for w in v:
                        newadd = etree.Element('field', name=k)
                        newadd.text = unicode(w)
                        doc.append(newadd)
    
    @property
    def cache(self):
        return self.cachedata
        
    @cache.setter
    def cache(self, value):
        if not isinstance(value, dict):
            raise Exception("Inferrer cache must be a dictionary.")
        if bool(self.cachedata) & isinstance(self.cachedata, dict):
            self.cachedata.update(value)
        else:
            self.cachedata = value