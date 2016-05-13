"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from lxml import etree

import Cfg
import Timer
import Utils
import hashlib
import html.entities
import logging
import os
import re
import shutil

import codecs
import sys

class Cleaner(object):
    """
    Corrects common errors in XML files and validates the file against an 
    external schema.
    """

    def __init__(self, output, source, update=False):
        self.hashIndex = {}
        self.log = logging.getLogger()
        # set parameters
        self.output = output
        self.source = source
        self.update = update
        
    def _fixEncoding(self, Text):
        try:
            outp = codecs.encode(codecs.decode(Text, 'utf-16le'), 'utf-8')
            return outp
        except:
            print((sys.exc_info()))
            
        
    def _fixAmpersands(self, Text):
        outp = re.sub(r'&(?![A-Za-z]+[0-9]*;|#[0-9]+;|#x[0-9a-fA-F]+;)', r'&amp;', Text)
        return outp

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
                        return chr(int(Text[3:-1], 16))
                    else:
                        return chr(int(Text[2:-1]))
                except ValueError:
                    pass
            else:
                # named entity  
                try:
                    Text = chr(html.entities.name2codepoint[Text[1:-1]])
                except KeyError:
                    pass
            return Text
        return re.sub("&#?\w+;", fixup, Html)

    def _removeEmptyDateFields(self, Text):
        """
        Remove any empty fromDate or toDate tags.
        """    
        try:
            xml = etree.XML(Text.encode('utf-8'))
            tree = etree.ElementTree(xml)
            for item in tree.findall('//fromDate'):
                if item.text is None:
                    item.getparent().remove(item)
            for item in tree.findall('//toDate'):
                if item.text is None:
                    item.getparent().remove(item)
            return etree.tostring(xml,pretty_print=True,encoding='unicode')
        except:
            self.log.error("Could not remove empty date fields: "+self.fn)
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
            return etree.tostring(xml,pretty_print=True,encoding='unicode')
        except:
            self.log.error("Could not remove empty standardDate fields: "+self.fn)
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
            self.log.error("Could not remove span tags: "+self.fn)
        finally:
            return Text
            
    def _removePreHeaderGarbage(self, Text):
        #Remove junk characters from the beginning of the XML file, before the <?xml> tag.
        return re.sub('^(.*?)<', '<', Text)

    def clean(self):
        """
        Read all files from source directory, apply fixes to common errors in 
        documents. Write cleaned files to the output directory.
        """
        # list of records that have been discovered
        records = []
        # for each file in the source folder
        for filename in os.listdir(self.source):
            #try:
                if filename.startswith('.'):
                    continue
                else:
                    records.append(filename)
                # read data
                #TODO: Add encoding param to Utils.read instead of copying this here.
                with open(self.source + os.sep + filename, 'r', encoding='utf-16-le') as f:
                    data = f.read().encode('utf-8').decode()
                #data = Utils.read(self.source, filename)
                #data.replace('\n', '').replace('\t', '')
                
                self.fn = filename
                fileHash = hashlib.sha1(data.encode('utf-8')).hexdigest()
                # if we are doing an update and the file has not changed then
                # skip it
                if self.update:
                    if filename in self.hashIndex and self.hashIndex[filename] == fileHash:
                        #self.log.info("No change since last update " + filename)
                        continue
                # record the file hash
                self.hashIndex[filename] = fileHash
                # fix problems
                if filename.endswith(".xml"):
                    data = self.fixEacCpf(data)
                elif filename.endswith(".htm") or filename.endswith(".html"):
                    data = self.fixHtml(data)
                else:
                    pass
                # write data to specified file in the output directory.
                outfile_path = self.output + os.sep + filename
                #print(outfile_path)
                with open(outfile_path,'w', encoding='utf-8') as outfile:
                    try:
                        outfile.write(data)
                    except:
                        print("FAIL: " + outfile_path)
                        shutil.copy(self.source + os.sep + filename, 'C:\\Users\\Adam_Bradley\\Projects\\eac.20160218.quar')
                #self.log.info("Stored document " + filename)
            #except Exception:
            #    self.log.error("Could not complete processing on " + filename, exc_info=Cfg.LOG_EXC_INFO)
        # return the list of processed records
        return records

    def fixEacCpf(self, Data):
        """
        Clean problems that are typical of EAC-CPF files.
        """
        #print(Data)
        # data = self._fixEntityReferences(data)
        #think I'm doing this in clean() now.
        #data = self._fixEncoding(Data)
        data = str(Data)
        data = self._fixAmpersands(data)
        data = self._removePreHeaderGarbage(data)
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
    
    def run(self):
        """
        Execute the clean operation using specified parameters.
        @todo this needs to be cleaned up and simplified
        """
        with Timer.Timer() as t:
            # create an index of file hashes, so that we can track what has changed
            if self.update:
                self.hashIndex = Utils.loadFileHashIndex(self.output)
            # clear output folder
            if not os.path.exists(self.output):
                os.makedirs(self.output)
            if not self.update:
                Utils.cleanOutputFolder(self.output)
            # check state
            assert os.path.exists(self.source), self.log.error("Source path does not exist: " + self.source)
            assert os.path.exists(self.output), self.log.error("Output path does not exist: " + self.output)
            # clean data
            records = self.clean()
            # remove records from the index that were deleted in the source
            if self.update:
                self.log.info("Clearing orphaned records from the file hash index")
                Utils.purgeIndex(records, self.hashIndex)
            # remove files from the output that are not in the index
            if self.update:
                self.log.info("Clearing orphaned files from the output folder")
                Utils.purgeFolder(self.output, self.hashIndex)
            # write the updated file hash index
            Utils.writeFileHashIndex(self.hashIndex, self.output)
        # log execution time
        self.log.info("Cleaner finished in {0}:{1}:{2}".format(t.hours, t.minutes, t.seconds))
        print(("Cleaner finished in {0}:{1}:{2}".format(t.hours, t.minutes, t.seconds)))


def clean(params, update=False):
    """
    Execute cleaning operations with specified parameters.
    """
    output = params.get("clean","output")
    source = params.get("clean","input")
    cleaner = Cleaner(output, source, update)
    cleaner.run()
