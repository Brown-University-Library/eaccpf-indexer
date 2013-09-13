"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from lxml import etree
import hashlib
import inspect
import logging
import os
import shutil
import urllib2
import yaml


log = logging.getLogger()

HASH_INDEX_FILENAME = '.index.yaml'


def cleanList(L):
    """
    Fix yaml encoding issues for list items.
    """
    for item in L:
        item = cleanText(item)
    return list

def cleanOutputFolder(Path, Update=False):
    """
    Clear all files from the output folder. If the folder does not exist
    then create it.
    """
    if not os.path.exists(Path):
        os.makedirs(Path)
        return
    if not Update:
        files = os.listdir(Path)
        for filename in files:
            path = Path + os.sep + filename
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

def cleanText(Val):
    """
    Fix yaml encoding issues for string items.
    """
    if Val == None:
        return ''
    clean = str(Val)
    clean = clean.strip()
    # clean = clean.replace('\n','')
    return clean

def fixIncorrectDateEncoding(Date):
    """
    Fix date string to make it conform to ISO standard.
    """
    if 'T00:00:00Z' in Date:
        return Date
    return Date + "T00:00:00Z"

def getFileHash(Path):
    """
    Get SHA1 hash of the specified file.
    """
    infile = open(Path,'r')
    data = infile.read()
    infile.close()
    return hashlib.sha1(data).hexdigest()

def getFileName(Url):
    """
    Get the filename from the specified URI or path.
    """
    name = str(Url)
    if 'http' and '?' in name:
        i = name.find('?')
        name = name[:i]
    if "/" in name:
        parts = name.split("/")
        return parts[-1]
    return name

def getFileNameExtension(Filename):
    """
    Get the filename extension. If an extension is not found, return ''.
    """
    if "." in Filename:
        parts = Filename.split(".")
        return parts[-1]
    return ''

def getFilenameWithAlternateExtension(Filename, Extension):
    """
    Returns the file name with the specified replacement extension.
    """
    name, _ = os.path.splitext(Filename)
    return name + "." + Extension

def isDigitalObjectYaml(Path):
    """
    Determines if the file at the specified path is an image record in
    YAML format.
    """
    if Path.endswith("yml"):
        infile = open(Path,'r')
        data = infile.read()
        infile.close()
        if "cache_id" in data:
            return True
    return False

def isInferredYaml(Path):
    """
    Determines if the file at the specified path is an inferred data
    record in YAML format.
    """
    if Path.endswith("yml"):
        return True
    return False

def isSolrInputDocument(Path):
    """
    Determines if the file at the specified path is a Solr Input
    Document.
    """
    if Path.endswith("xml"):
        infile = open(Path, 'r')
        data = infile.read()
        infile.close()
        if "<doc>" in data and "</doc>" in data:
            return True
    return False

def isUrl(Path):
    """
    Determine if the source is a URL or a file system path.
    """
    if Path != None and ("http:" in Path or "https:" in Path):
        return True
    return False

def loadFileHashIndex(Path):
    """
    Load the file hash index from the specified path.
    """
    if os.path.exists(Path + os.sep + HASH_INDEX_FILENAME):
        infile = open(Path + os.sep + HASH_INDEX_FILENAME,'r')
        data = infile.read()
        index = yaml.load(data)
        infile.close()
        if index != None:
            return index
    return {}

def loadTransform(Path):
    """
    Load the specified XSLT file and return an LXML transformer.
    """
    xslt_file = open(Path, 'r')
    xslt_data = xslt_file.read()
    xslt_root = etree.XML(xslt_data)
    xslt_file.close()
    try:
        return etree.XSLT(xslt_root)
    except:
        log.error("Could not load XSLT file {0}".format(Path))

def purgeFolder(Folder, HashIndex):
    """
    Purge all files in folder not represented in the index.
    """
    files = os.listdir(Folder)
    for filename in files:
        if not filename in HashIndex.keys():
            os.remove(Folder + os.sep + filename)

def purgeIndex(Records, HashIndex):
    """
    Purge all index entries not represented in the record list.
    """
    rtd = []
    for filename in HashIndex.keys():
        if filename not in Records:
            rtd.append(filename)
        for filename in rtd:
            del HashIndex[filename]
    return HashIndex

def read(Path, Filename):
    """
    Read string data from file.
    """
    infile = open(Path + os.sep + Filename,'r')
    data = infile.read()
    infile.close()
    return data

def readYaml(Path, Filename):
    """
    Load the specified YAML data file.
    """
    infile = open(Path + os.sep + Filename, 'r')
    yml = yaml.load(infile)
    infile.close()
    return yml

def resourceExists(Resource):
    """
    Determine if a resource exists. The resource may be specified as a file
    system path or URL.
    """
    if 'http://' in Resource or 'https://' in Resource:
        try:
            urllib2.urlopen(Resource)
            return True
        except:
            return False
    else:
        if os.path.exists(Resource):
            return True
        else:
            return False

def tryReadYaml(Path, Filename):
    """
    Try to load the specified data file. If it does not exist, return an empty
    dictionary.
    """
    try:
        infile = open(Path + os.sep + Filename, 'r')
        record = yaml.load(infile)
        infile.close()
        if record != None:
            return record
    except:
        pass
    return {}

def validate(Source, Schema):
    """
    Validate a collection of files against an XML schema.
    """
    try:
        # load schemas
        infile = open(Schema, 'r')
        schema_data = infile.read()
        schema_root = etree.XML(schema_data)
        schema = etree.XMLSchema(schema_root)
        infile.close()
        # create validating parser
        parser = etree.XMLParser(schema=schema)
        # validate files against schema
        files = os.listdir(Source)
        for filename in files:
            infile = open(Source + os.sep + filename,'r')
            data = infile.read()
            infile.close()
            try:
                etree.fromstring(data, parser)
            except:
                pass
    except:
        pass

def write(Path, Filename, Data):
    """
    Write the string to the file in the specified path.
    """
    outfile = open(Path + os.sep + Filename, 'w')
    outfile.write(Data)
    outfile.close()

def writeFileHashIndex(Data, Path):
    """
    Write the file hash index to the specified path.
    """
    writeYaml(Path, HASH_INDEX_FILENAME, Data)

def writeYaml(Path, Filename, Data):
    """
    Write data in Yaml format to the filename in path.
    """
    try:
        outfile = open(Path + os.sep + Filename, 'w')
        yaml.dump(Data, outfile)
        outfile.close()
    except:
        pass # need to log error