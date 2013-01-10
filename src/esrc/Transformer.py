'''
This file is subject to the terms and conditions defined in the
'LICENSE.txt' file, which is part of this source code package.
'''

import logging
import os 
import re
import sys

class Transformer(object):
    '''
    Transforms an XML file using an external XSLT transform.
    '''

    def __init__(self,params):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('feeder')

    def _apply_doc_boost(self, doc, boost):
        if boost is not None:
            for b in boost:
                if re.search(b, self.document):
                    doc.xpath('//add/doc')[0].set("boost", str(boost[b]))

    def _apply_field_boosts(self, doc, boost):
        if boost is not None:
            for b in boost:
                searchfor = "//add/doc/field[@name='" + b + "']"
            try:
                doc.xpath(searchfor)[0].set("boost", str(boost[b]))
            except:
                pass
        
    def _load_HTML(self, file):
        """ Take a file arg, load it, then use etree.HTML to process it.
            Returns a tree suitable for use in a transform
        """
        # is it a file, can we read it?
        if os.path.isfile(file):
            try:
                f = open(file)
                tree = etree.HTML(f.read())
                f.close()
                return tree
            except IOError:
                print "Can't seem to read: " + file
                sys.exit(0)

    def _load_transform(self, file):
        """ Load a transform and return it to the caller
        """
        # is it a file, can we read it?
        if os.path.isfile(file):
            try:
                xslt = etree.parse(file,self.parser)
                return etree.XSLT(xslt)
            except:
                print "Can't seem to read: " + file
                sys.exit(0)

    def _merge(self, doc, eac):
        for field in eac.xpath('/doc')[0].iterchildren():
            # then cycle through each element adding it to the other doc
            #print etree.tostring(field)
            etree.SubElement(doc.xpath('/add/doc')[0], field.tag, name=field.attrib['name']).text = field.text
        
    def run(self, params):
        
        pass
    
    def transform(self, source, output, report=None):
        #print config['transform']

        # read in the XSL transform for the HTML file we've just been given
        #  and produce the transformer
        transform = self._load_transform(config['transform'])

        # read the document to be transformed
        tree = self._load_HTML(self.document)

        # transform the document
        solr_doc = transform(tree)
        if self._check_HTML_transform(solr_doc):
            sys.exit(0)

        # see if an EAC file is ref'ed
        try:
           eac_file = solr_doc.xpath("//add/doc/field[@name='EAC']")[0].text
        except:
           eac_file = None
        #print eac_file
        if eac_file is not None:
            # load and prepare the transform for the EAC file
            transform = self._load_transform(config['eac-transform'])

            # get the eac file
            resp, content  = Http().request(eac_file, "GET")
            if resp['status'] == '200' and resp['content-type'] == "application/xml":
                # if it loaded ok - and it looks like an xml file (which it should be)
                #  parse it and transform it
                tree = etree.parse(StringIO(content), self.parser)
                #print etree.tostring(xml, pretty_print=True)
                eac_doc = transform(tree)
                if self._check_EAC_transform(eac_doc):
                    sys.exit(0)
                self._merge(solr_doc, eac_doc)

        self._apply_doc_boost(solr_doc, config['boost-docs'])
        self._apply_field_boosts(solr_doc, config['boost-fields'])

        # and store the document 
        self.doc = solr_doc
    
    def validate(self, source, output, schema, report=None):
        pass
    
    