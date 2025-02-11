"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from lxml import etree

import Cfg
import calendar
import datetime
import hashlib
import logging
import os
import shutil
import tempfile
import urllib.request, urllib.error, urllib.parse
import urllib.parse
import yaml
import sys

log = logging.getLogger()


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
        for filename in os.listdir(Path):
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

def getCommonStartString(A, B):
    """
    Get the common starting substring for strings A and B.
    """
    common = []
    i = 0
    while i < len(A) and i < len(B):
        if A[i] == B[i]:
            common.append(A[i])
        else:
            break
        i += 1
    return ''.join(common)

def getFileHash(Path, Filename=None):
    """
    Get a SHA1 hash of the specified file.
    """
    path = Path + os.sep + Filename if Filename else Path
    with open(path,'r') as f:
        data = f.read()
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
    _, ext = os.path.splitext(Filename)
    return ext.replace('.', '')

def getFilenameWithAlternateExtension(Filename, Extension):
    """
    Returns the file name with the specified replacement extension. The
    file extension should specified without leading period character.
    """
    name, _ = os.path.splitext(Filename)
    return "{0}.{1}".format(name, Extension)

def getRecordIdFromFilename(Filename):
    """
    Get the record ID from a filename. The record ID is the filename without
    the three character extension.
    """
    name, _ = os.path.splitext(Filename)
    return name

def getTemporaryFileFromResource(source):
    """
    Retrieve the web or file system resource and write it to a temporary file
    in the local file system. Return the path to the temporary file.
    """
    ext = getFileNameExtension(source)
    temp = tempfile.mktemp(suffix=".{0}".format(ext))
    if 'http://' in source or 'https://' in source:
        response = urllib.request.urlopen(source)
        data = response.read()
        with open(temp, 'wb') as f:
            f.write(data)
    else:
        shutil.copy(source, temp)
    return temp

def isDigitalObjectYaml(Path, Filename=None):
    """
    Determines if the file at the specified path is an image record in
    YAML format.
    """
    path = Path + os.sep + Filename if Filename else Path
    if path.endswith(".yml"):
        with open(path,'r') as f:
            data = f.read()
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
        with open(Path, 'r') as f:
            data = f.read()
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

def loadFileHashIndex(Path, Filename=Cfg.HASH_INDEX_FILENAME):
    """
    Load the file hash index from the specified path.
    """
    if os.path.exists(Path + os.sep + Filename):
        with open(Path + os.sep + Filename,'r') as f:
            data = f.read()
            index = yaml.load(data)
        if index != None:
            return index
    return {}

def load_from_source(Source):
    """
    Load text data from the specified source.
    """
    if 'http://' in Source or 'https://' in Source:
        response = urllib.request.urlopen(Source)
        data = response.read()
        # data = unicode(data, errors='replace')
    else:
        assert os.path.exists(Source), "Resource does not exist {0}".format(Source)
        with open(Source, 'r') as f:
            data = f.read()
            # data = unicode(data, errors='replace')
    # the lxml parser won't accept unicode encoded strings and throws an
    # exception. pass it a str instead
    return str(data)

def loadTransform(Path):
    """
    Load the specified XSLT file and return an LXML transformer.
    """
    with open(Path, 'r') as f:
        xslt_data = f.read()
    xslt_root = etree.XML(xslt_data)
    outp = etree.XSLT(xslt_root)
    return outp
    

def map_url_to_local_path(url, site_root_path):
    """
    Determine the local file system path to a file, given a local path to the
    root of a web site and a URL to the file resource in question.
    """
    parsed = urllib.parse.urlparse(url)
    path = site_root_path + os.sep + parsed.path
    abs_path = os.path.abspath(path)
    # if the abs_path is above the site_root_path, then return the
    # site_root_path
    if not os.path.commonprefix([site_root_path, abs_path]) == site_root_path:
        return site_root_path
    return abs_path

def parseUnitDate(Date):
    """
    Parse unit date field to produce fromDate and toDate field values.
    @todo need to match c. 1900 - c. 1930
    """
    formats = [
        "%Y-%m-%d", # 1976-01-01
        "%Y %m %d", # 1976 01 01
        "%d %B %Y", # 12 January 1997
        "%B %Y",    # February 1998
        "%Y",       # 2004
        "c. %Y",    # c. 2004
        "c.%Y",     # c.2004
        "c %Y",     # c 2004
        "c%Y",      # c2004
        "circa %Y", # circa 2004
        "%Y?",      # 2004?
    ]
    Date = Date.replace('?', '')
    for i in range(len(formats)):
        try:
            f = formats[i]
            fromDate = datetime.datetime.strptime(Date, f)
            toDate = datetime.datetime.strptime(Date, f)
            if i > 2:
                _, day = calendar.monthrange(toDate.year, toDate.month)
                toDate = toDate.replace(day=day)
            if i > 3:
                toDate = toDate.replace(month=12)
            fromDate = "{0}Z".format(str(fromDate).replace(' ', 'T'))
            toDate = "{0}Z".format(str(toDate).replace(' 00:00:00', 'T23:59:59'))
            # ensure that the new date conforms to Solr's requirements
            _ = datetime.datetime.strptime(fromDate, "%Y-%m-%dT%H:%M:%SZ")
            _ = datetime.datetime.strptime(toDate, "%Y-%m-%dT%H:%M:%SZ")
            return fromDate, toDate
        except:
            pass
    return None, None

def purgeFolder(path, file_index):
    """
    Purge all files in path not represented in the file index.
    """
    keys = list(file_index.keys())
    for filename in [f for f in os.listdir(path) if f not in keys]:
        file_path = path + os.sep + filename
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path, ignore_errors=True)
        log.debug("Purged {0} from cache folder".format(filename))

def purgeIndex(file_list, file_hash_index):
    """
    Purge all file hash entries not represented in the file list.
    """
    for filename in [filename for filename in list(file_hash_index.keys()) if filename not in file_list]:
        del file_hash_index[filename]
        log.debug("Purged {0} from cache index".format(filename))
    return file_hash_index

def read(Path, Filename):
    """
    Read string data from file.
    """
    with open(Path + os.sep + Filename,'r') as f:
        data = f.read()
    return data

def readYaml(Path, Filename):
    """
    Load the specified YAML data file.
    """
    with open(Path + os.sep + Filename, 'r') as f:
        yml = yaml.load(f)
    return yml

def resourceExists(Resource):
    """
    Determine if a resource exists. The resource may be specified as a file
    system path or URL.
    """
    if 'http://' in Resource or 'https://' in Resource:
        try:
            urllib.request.urlopen(Resource)
            return True
        except:
            return False
    else:
        return True if os.path.exists(Resource) else False

def strip_quotes(S):
    """
    String leading and trailing quotation marks
    """
    if '"' in S[0] or "'" in S[0]:
        S = S[1:]
    if '"' in S[-1] or "'" in S[-1]:
        S = S[:-1]
    return S

def tryReadYaml(Path, Filename):
    """
    Try to load the specified data file. If it does not exist, return an empty
    dictionary.
    """
    try:
        with open(Path + os.sep + Filename, 'r') as f:
            record = yaml.load(f)
        if record != None:
            return record
    except:
        pass
    return {}

def urlToFileSystemPath(Url, FileSystemBase):
    """
    Attempt to translate the URL to a local file system path. The file system
    base is the root of the web site. This method assumes that the file system
    base corresponds with the root of the web site.
    """
    # remove the host and domain portion of the URL
    parts = urllib.parse.urlparse(Url)
    if FileSystemBase.endswith('/'):
        FileSystemBase = FileSystemBase[:-1]
    return "{0}{1}".format(FileSystemBase, parts.path)

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
            with open(Source + os.sep + filename,'r') as f:
                data = f.read()
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
    with open(Path + os.sep + Filename, 'w') as f:
        f.write(Data)

def writeFileHashIndex(Data, Path, Filename=Cfg.HASH_INDEX_FILENAME):
    """
    Write the file hash index to the specified path.
    """
    writeYaml(Path, Filename, Data)

def writeYaml(Path, Filename, Data):
    """
    Write data in YAML format to the specified path.
    """
    with open(Path + os.sep + Filename, 'w') as f:
        yaml.dump(Data, f, default_flow_style=False)