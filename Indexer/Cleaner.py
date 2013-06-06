"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from BeautifulSoup import BeautifulSoup
from lxml import etree
import htmlentitydefs
import logging
import os
import re
import yaml


class Cleaner():
    """
    Corrects common errors in XML files and validates the file against an 
    external schema.
    """

    def __init__(self):
        """
        Initialize the class
        """
        self.hashIndexFilename = ".index.yml"
        self.logger = logging.getLogger('Cleaner')
        
    def _cleanOutput(self, Path):
        """
        Clear all files from the output folder. If the folder does not exist
        then create it.
        """
        if os.path.exists(Path):
            files = os.listdir(Path)
            for filename in files:
                os.remove(Path + os.sep + filename)
        else:
            os.makedirs(Path)
        self.logger.info("Cleared output folder at " + Path)

    def _convertHTMLEntitiesToUnicode(self, text):
        """
        Converts HTML entities to unicode.  For example '&amp;' becomes '&'.
        """
        text = unicode(BeautifulSoup(text, convertEntities=BeautifulSoup.ALL_ENTITIES))
        return text    

    def _fixAttributeURLEncoding(self,xml):
        """
        Where an XML tag contains an attribute with a URL in it, any 
        ampersand characters in the URL must be escaped.
        @todo: finish implementing this method
        @see http://priyadi.net/archives/2004/09/26/ampersand-is-not-allowed-within-xml-attributes-value/
        """
        return xml

    def _fixDateFields(self,xml):
        """
        Convert dates into ISO format. Where a date is specified with a circa 
        indication, or 's to indicate a decade, expand the date into a range.
        @todo: finish implementing this method
        """
        return xml
   
    def _fixEntityReferences(self, Html):
        """
        Convert HTML entities into XML entities.
        @see http://effbot.org/zone/re-sub.htm#unescape-html
        """
        def fixup(m):
            Text = m.group(0)
            if Text[:2] == "&#":
                # character reference
                try:
                    if Text[:3] == "&#x":
                        return unichr(int(Text[3:-1], 16))
                    else:
                        return unichr(int(Text[2:-1]))
                except ValueError:
                    pass
            else:
                # named entity
                try:
                    Text = unichr(htmlentitydefs.name2codepoint[Text[1:-1]])
                except KeyError:
                    pass
            return Text
        return re.sub("&#?\w+;", fixup, Html)

    def _getSourceAndReferrerValues(self, Path):
        """
        Get source, metadata and presentation URL values from comment embedded
        in the document.
        """
        infile = open(Path,'r')
        lines = infile.readlines()
        infile.close()
        for line in lines:
            try:
                src = line.index("@source")
                meta = line.index("@metadata")
                pres = line.index("@presentation")
                source = line[src+len("@source="):meta-1]
                metadata = line[meta+len("@metadata="):pres-1]
                presentation = line[pres+len("@presentation="):-4]
                return (source, metadata, presentation)
            except:
                pass
        # default case
        return ('', '', '')
    
    def _loadFileHashIndex(self, Path):
        """
        Load the file hash index from the specified path.
        """
        if os.path.exists(Path + os.sep + self.hashIndexFilename):
            infile = open(Path + os.sep + self.hashIndexFilename,'r')
            data = infile.read()
            index = yaml.load(data)
            infile.close()
            if index != None:
                return index
        return {}

    def _removeEmptyDateFields(self, Text):
        """
        Remove any empty fromDate or toDate tags.
        """
        xml = etree.XML(Text)
        tree = etree.ElementTree(xml)
        for item in tree.findall('//fromDate'):
            if item.text is None or item.text == '':
                item.getparent().remove(item)
        for item in tree.findall('//toDate'):
            if item.text is None or item.text == '':
                item.getparent().remove(item)
        return etree.tostring(xml,pretty_print=True)
    
    def _removeEmptyStandardDateFields(self, Text):
        """
        Remove any fromDate or toDate tags that have empty standardDate attributes.
        """
        xml = etree.XML(Text)
        tree = etree.ElementTree(xml)
        for item in tree.findall('//fromDate'):
            date = item.attrib['standardDate']
            if date is None or date == '':
                item.attrib.pop('standardDate')
        for item in tree.findall('//toDate'):
            date = item.attrib['standardDate']
            if date is None or date == '':
                item.attrib.pop('standardDate')
        return etree.tostring(xml,pretty_print=True)
    
    def _removeSpanTags(self, Text):
        """
        Remove all <span> and </span> tags from the markup.
        """
        # replace simple cases first
        Text = Text.replace("<span>","")
        Text = Text.replace("</span>","")
        # replace spans with attributes
        for span in re.findall("<span \w*=\".*\">",Text):
            Text = Text.replace(span,'')
        return Text

    def _writeFileHashIndex(self, Data, Path):
        """
        Write the file hash index to the specified path.
        """
        outfile = open(Path + os.sep + self.hashIndexFilename,'w')
        yaml.dump(Data,outfile)
        outfile.close()

    def cleanFile(self, Source, Output):
        """
        Read the input file, apply fixes to common errors, then write the file
        to the output.
        """
        files = os.listdir(Source)
        for filename in files:
            try:
                # read data
                infile = open(Source + os.sep + filename,'r')
                data = infile.read()
                infile.close()
                # fix problems
                if filename.endswith(".xml"):
                    # the source/referrer values comment gets deleted by the XML
                    # parser, so we'll save it here temporarily while we do our cleanup
                    src, meta, pres = self._getSourceAndReferrerValues(Source + os.sep + filename)
                    data = self.fixEacCpf(data)
                    # write source/referrer comment back at the end of the file
                    data += '\n<!-- @source=%(source)s @metadata=%(metadata)s @presentation=%(presentation)s -->' % {"source":src, "metadata": meta, "presentation":pres}
                elif filename.endswith(".htm") or filename.endswith(".html"):
                    data = self.fixHtml(data)
                else:
                    pass
                # write data to specified file in the output directory.
                outfile_path = Output + os.sep + filename
                outfile = open(outfile_path,'w')
                outfile.write(data)
                outfile.close()
                self.logger.info("Stored document " + filename)
            except Exception:
                self.logger.warning("Could not complete processing on " + filename, exc_info=True)

    def clean(self, Source, Output, Update):
        """
        Read all files from source directory, apply fixes to common errors in 
        documents. Write cleaned files to the output directory.
        """
        files = os.listdir(Source)
        for filename in files:
            try:
                # read data
                infile = open(Source + os.sep + filename,'r')
                data = infile.read()
                infile.close()        
                # fix problems
                if filename.endswith(".xml"):
                    # the source/referrer values comment gets deleted by the XML 
                    # parser, so we'll save it here temporarily while we do our cleanup
                    src, meta, pres = self._getSourceAndReferrerValues(Source + os.sep + filename)
                    data = self.fixEacCpf(data)
                    # write source/referrer comment back at the end of the file
                    data += '\n<!-- @source=%(source)s @metadata=%(metadata)s @presentation=%(presentation)s -->' % {"source":src, "metadata": meta, "presentation":pres}
                elif filename.endswith(".htm") or filename.endswith(".html"):
                    data = self.fixHtml(data)
                else:
                    pass
                # write data to specified file in the output directory.
                outfile_path = Output + os.sep + filename
                outfile = open(outfile_path,'w')
                outfile.write(data)
                outfile.close()
                self.logger.info("Stored document " + filename)
            except Exception:
                self.logger.warning("Could not complete processing on " + filename, exc_info=True)
        
    def fixEacCpf(self, Data):
        """
        Clean problems that are typical of EAC-CPF files.
        """
        # data = self._fixEntityReferences(data)
        data = self._fixAttributeURLEncoding(Data)
        data = self._fixDateFields(data)
        data = self._removeSpanTags(data)
        data = self._removeEmptyDateFields(data)
        data = self._removeEmptyStandardDateFields(data) # XML needs to be valid before we can do this
        return data
    
    def fixHtml(self, Data):
        """
        Clean typical problems found in HTML files.
        """
        data = self._convertHTMLEntitiesToUnicode(Data)
        return data
    
    def run(self, Params, Update=False):
        """
        Execute the clean operation using specified parameters.
        """
        # get parameters
        source = Params.get("clean","input")
        output = Params.get("clean","output")
        # load filename to hash index. we use this to keep track of which files
        # have changed
        hashIndex = {}
        if Update:
            hashIndex = self._loadFileHashIndex(output)
        # clear output folder
        if not Update:
            self._cleanOutput(output)
        # check state
        assert os.path.exists(source), self.logger.warning("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.warning("Output path does not exist: " + output)
        # clean data
        records = self.clean(source, output, Update)
        # remove records from the index that were deleted in the source
        if Update:
            self.logger.info("Clearing orphaned records from the file hash index")
            rtd = []
            for filename in hashIndex.keys():
                if filename not in records:
                    rtd.append(filename)
            for filename in rtd:
                del hashIndex[filename]
        # remove files from the output that are not in the index
        if Update:
            self.logger.info("Clearing orphaned files from the output folder")
            files = os.listdir(output)
            for filename in files:
                if not filename in hashIndex.keys():
                    os.remove(output + os.sep + filename)
        # write the updated file hash index
        self._writeFileHashIndex(hashIndex, output)
