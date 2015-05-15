from lxml import etree
import yaml

class Inferrer(object):
    """
        This is an abstract class. Inferrers' class names must begin with 'uf' and end with '_Inferrer'
    """
    
    def infer(self, xml, sleep):
        """
            The infer method should return a dictionary of content that will be 
            converted to YAML and saved in the inferred data file for the XML document xml.
            
            If infer() does anything that should cause the Facter script to sleep temporarily,
            infer should append True to sleep.
        """
        pass
    
    def append(self, inferred, xml):
        """
            inferred is the dictionary saved from infer. Insert this data into xml. Return values are ignored.
            
            This method just creates a new node for each item in the dictionary. It's probably
            what you want in most cases.
        """
        doc = xml.getchildren()[0]
        
        for k,v in inferred.items():
            newadd = etree.Element('field', name=k)
            newadd.text = v
            doc.append(newadd)