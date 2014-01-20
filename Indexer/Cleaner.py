"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from lxml import etree
import Utils
import hashlib
import htmlentitydefs
import logging
import os
import re

LOG_EXC_INFO = False


class Cleaner(object):
    """
    Corrects common errors in XML files and validates the file against an 
    external schema.
    """

    def __init__(self):
        """
        Initialize
        """
        self.hashIndexFilename = ".index.yml"
        self.logger = logging.getLogger()
        
    def _fixAttributeURLEncoding(self, Xml):
        """
        Where an XML tag contains an attribute with a URL in it, any 
        ampersand characters in the URL must be escaped.
        @todo: finish implementing this method
        @see http://priyadi.net/archives/2004/09/26/ampersand-is-not-allowed-within-xml-attributes-value/
        """
        return Xml

    def _fixDateFields(self, Xml):
        """
        Convert dates into ISO format. Where a date is specified with a circa 
        indication, or 's to indicate a decade, expand the date into a range.
        @todo: finish implementing this method
        """
        return Xml
   
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

    def _removeEmptyDateFields(self, Text):
        """
        Remove any empty fromDate or toDate tags.
        """
        try:
            xml = etree.XML(Text)
            tree = etree.ElementTree(xml)
            for item in tree.findall('//fromDate'):
                if item.text is None:
                    item.getparent().remove(item)
            for item in tree.findall('//toDate'):
                if item.text is None:
                    item.getparent().remove(item)
            return etree.tostring(xml,pretty_print=True)
        except:
            self.logger.error("Could not remove empty date fields")
            return Text
    
    def _removeEmptyStandardDateFields(self, Text):
        """
        Remove any fromDate or toDate tags that have empty standardDate attributes.
        """
        try:
            xml = etree.XML(Text)
            tree = etree.ElementTree(xml)
            for item in tree.findall('//fromDate'):
                if 'standardDate' in item.attrib and item.attrib['standardDate'] is None:
                    item.attrib.pop('standardDate')
            for item in tree.findall('//toDate'):
                if 'standardDate' in item.attrib and item.attrib['standardDate'] is None:
                    item.attrib.pop('standardDate')
            return etree.tostring(xml,pretty_print=True)
        except:
            self.logger.error("Could not remove empty standardDate fields")
            return Text
    
    def _removeSpanTags(self, Text):
        """
        Remove all <span> and </span> tags from the markup.
        """
        try:
            # replace simple cases first
            Text = Text.replace("<span>","")
            Text = Text.replace("</span>","")
            # replace spans with attributes
            for span in re.findall("<span \w*=\".*\">",Text):
                Text = Text.replace(span,'')
        except:
            self.logger.error("Could not remove span tags")
        finally:
            return Text

    def clean(self, Source, Output, HashIndex, Update):
        """
        Read all files from source directory, apply fixes to common errors in 
        documents. Write cleaned files to the output directory.
        """
        # list of records that have been discovered
        records = []
        # for each file in the source folder
        for filename in os.listdir(Source):
            try:
                if filename.startswith('.'):
                    continue
                else:
                    records.append(filename)
                # read data
                data = Utils.read(Source, filename)
                fileHash = hashlib.sha1(data).hexdigest()
                # if we are doing an update and the file has not changed then
                # skip it
                if Update:
                    if filename in HashIndex and HashIndex[filename] == fileHash:
                        self.logger.info("No change since last update " + filename)
                        continue
                # record the file hash
                HashIndex[filename] = fileHash
                # fix problems
                if filename.endswith(".xml"):
                    data = self.fixEacCpf(data)
                elif filename.endswith(".htm") or filename.endswith(".html"):
                    data = self.fixHtml(data)
                else:
                    pass
                # write data to specified file in the output directory.
                outfile_path = Output + os.sep + filename
                with open(outfile_path,'w') as outfile:
                    outfile.write(data)
                self.logger.info("Stored document " + filename)
            except Exception:
                self.logger.error("Could not complete processing on " + filename, exc_info=LOG_EXC_INFO)
        # return the list of processed records
        return records

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
        # data = Data.decode('utf-8','xmlcharrefreplace')
        # data = Data.decode('utf-8', 'ignore')
        # I don't like this either but it appears to be the only
        # thing that works for some reason
        data = str(Data)
        data = data.replace('&', 'and')
        return data
    
    def run(self, Params, Update=False, StackTrace=False):
        """
        Execute the clean operation using specified parameters.
        @todo this needs to be cleaned up and simplified
        """
        # get parameters
        source = Params.get("clean","input")
        output = Params.get("clean","output")
        # create an index of file hashes, so that we can track what has changed
        hashIndex = {}
        if Update:
            hashIndex = Utils.loadFileHashIndex(output)
        # clear output folder
        if not os.path.exists(output):
            os.makedirs(output)
        if not Update:
            Utils.cleanOutputFolder(output)
        # check state
        assert os.path.exists(source), self.logger.error("Source path does not exist: " + source)
        assert os.path.exists(output), self.logger.error("Output path does not exist: " + output)
        # clean data
        records = self.clean(source, output, hashIndex, Update)
        # remove records from the index that were deleted in the source
        if Update:
            self.logger.info("Clearing orphaned records from the file hash index")
            Utils.purgeIndex(records, hashIndex)
        # remove files from the output that are not in the index
        if Update:
            self.logger.info("Clearing orphaned files from the output folder")
            Utils.purgeFolder(output, hashIndex)
        # write the updated file hash index
        Utils.writeFileHashIndex(hashIndex, output)
