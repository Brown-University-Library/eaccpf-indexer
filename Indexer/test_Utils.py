"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

import os
import random
import string
import tempfile
import unittest
import Utils


class TestUtils(unittest.TestCase):
    pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cleanList(self):
        pass

    def test_cleanOutputFolder(self):
        """
        It should confirm that the path exists and create it if it does not. In
        the case where the path exists, it contains existing files, and we have
        not passed Update=True, it should clear the contents of the folder.
        """
        # existing path with no files
        temp1 = tempfile.mktemp()
        os.mkdir(temp1)
        Utils.cleanOutputFolder(temp1)
        self.assertEquals(os.path.exists(temp1), True)
        # existing path with files, no update
        temp2 = tempfile.mktemp()
        os.mkdir(temp2)
        names = ['a.test','b.test','c.test']
        for name in names:
            with open(temp2 + os.sep + name, 'w') as f:
                f.write("-----")
        Utils.cleanOutputFolder(temp2)
        self.assertEquals(os.path.exists(temp2), True)
        files = os.listdir(temp2)
        self.assertEqual(len(files), 0)
        # existing path with files, update
        temp3 = tempfile.mktemp()
        os.mkdir(temp3)
        names = ['a.test','b.test','c.test']
        for name in names:
            with open(temp3 + os.sep + name, 'w') as f:
                f.write("-----")
        Utils.cleanOutputFolder(temp3, Update=True)
        self.assertEquals(os.path.exists(temp3), True)
        files = os.listdir(temp3)
        self.assertEquals(len(files), len(names))
        # pass it a directory name that does not exist
        # it should create the directory
        temp4 = tempfile.gettempdir() + os.sep + "testdir0000000"
        self.assertEquals(os.path.exists(temp4), False)
        Utils.cleanOutputFolder(temp4)
        self.assertEquals(os.path.exists(temp4), True)
        # clean up
        try:
            import shutil
            shutil.rmtree(temp1)
            shutil.rmtree(temp2)
            shutil.rmtree(temp3)
            shutil.rmtree(temp4)
        except:
            pass

    def test_cleanText(self):
        """
        It should convert a null string to an empty string value. It should
        remove preceeding and trailing whitespace from a string.
        """
        s1 = None
        s2 = Utils.cleanText(s1)
        self.assertNotEqual(s2, None)
        self.assertEquals(s2, '')

        s1 = " This is a long sentence with trailing whitespace.     "
        s2 = Utils.cleanText(s1)
        self.assertNotEqual(s2, None)
        self.assertNotEqual(len(s1), len(s2))
        self.assertNotEqual(s2[0], ' ')

    def test_fixIncorrectDateEncoding(self):
        pass

    def test_getCommonStartingSubstring(self):
        """
        It should return the common starting part of two strings.
        """
        cases = [
            ("http://www.example.com/path/to/A", "http://www.example.com/path/to/B", "http://www.example.com/path/to/")
        ]
        for case in cases:
            a, b, common = case
            result = Utils.getCommonStartString(a, b)
            self.assertEquals(result, common)

    def test_getFileHash(self):
        pass

    def test_getFileName(self):
        """
        It should return the filename portion of the URL
        """
        cases = [
            ("http://docs.python.org/2/library/string.html", "string.html"),
            ("https://web.esrc.unimelb.edu.au/wiki/doku.php?id=findandconnectnew&s[]=facp", "doku.php"),
            ("/path/to/the/file.test", "file.test"),
            ("/file.test", "file.test"),
            ("file.test", "file.test")
        ]
        for case in cases:
            url, filename = case
            fn = Utils.getFileName(url)
            self.assertEqual(filename, fn)

    def test_getFileNameExtension(self):
        """
        It should return the one or more character extension following the last
        dot '.' in the filename.  If the filename does not have an extension,
        it should return ''
        """
        cases = [
            ("this.is.a.complex.filename.abc", "abc"),
            ("thisfilehasnoextension", "")
        ]
        for case in cases:
            name, ext = case
            x = Utils.getFileNameExtension(name)
            self.assertEquals(ext, x)

    def test_getFileNameWithAlternateExtension(self):
        """
        It should return the filename with any existing file extension replaced
        with the value provided.
        """
        cases = [
            ("thisismyfile.txt", "yml", "thisismyfile.yml"),
            ("thisismyfile.yml", "abc", "thisismyfile.abc"),
            ("thisismyfile", "yml", "thisismyfile.yml")
        ]
        for case in cases:
            filename, ext, newname = case
            renamed = Utils.getFilenameWithAlternateExtension(filename, ext)
            self.assertEquals(newname, renamed)

    def test_isDigitalObjectYaml(self):
        """
        It should determine if a file is in YAML format, and if it represents a
        digital object.
        """
        cases = [

        ]
        for case in cases:
            path, isdobj = case
            is_dobj = Utils.isDigitalObjectYaml(path)
            self.assertEquals(isdobj, is_dobj)

    def test_isInferredYaml(self):
        """
        It should determine if a file is in YAML format and if it represents
        inferred data.
        """
        pass

    def test_isSolrInputDocument(self):
        """
        It should determine if a file is a Solr Input Document.
        """
        pass

    def test_isUrl(self):
        """
        It should determine if a string is a URL.
        """
        cases = [
            ("http://example.com:8080/path/to/file", True),
            ("https://example.com:8080/path/to/file", True),
            ("ftp://example.com:8080/path/to/file", False),
            ("/path/to/my/file", False)
        ]
        for case in cases:
            url, isurl = case
            is_url = Utils.isUrl(url)
            self.assertEquals(isurl, is_url)

    def test_loadFileHashIndex(self):
        pass

    def test_parseUnitDate(self):
        """
        Parse unit date value into fromDate, toDate values.
        """
        cases = [
            ('1976-03-05','1976-03-05T00:00:00Z','1976-03-05T23:59:59Z'),
            ('1976 03 05','1976-03-05T00:00:00Z','1976-03-05T23:59:59Z'),
            ('5 March 1976','1976-03-05T00:00:00Z','1976-03-05T23:59:59Z'),
            ('March 1976','1976-03-01T00:00:00Z','1976-03-31T23:59:59Z'),
            ('1976','1976-01-01T00:00:00Z','1976-12-31T23:59:59Z'),
            ('c.1960','1960-01-01T00:00:00Z','1960-12-31T23:59:59Z'),
            ('c. 1960','1960-01-01T00:00:00Z','1960-12-31T23:59:59Z'),
            ('c 1960','1960-01-01T00:00:00Z','1960-12-31T23:59:59Z'),
            ('circa 1960','1960-01-01T00:00:00Z','1960-12-31T23:59:59Z'),
            # ('c. 1900 - c. 1930', '1900-01-01T00:00:00Z','1930-12-31T23:59:59Z') # @todo this case is not currently supported
        ]
        for case in cases:
            unitDate, fromDate, toDate = case
            r_fromDate, r_toDate = Utils.parseUnitDate(unitDate)
            self.assertEquals(fromDate, r_fromDate)
            self.assertEquals(toDate, r_toDate)

    def test_purgeFolder(self):
        pass

    def test_purgeIndex(self):
        pass

    def test_read(self):
        pass

    def test_readYaml(self):
        pass

    def test_resourceExists(self):
        pass

    def test_strip_quotes(self):
        """
        It should return the source string with leading and trailing quotation
        marks removed.
        """
        cases = [
            ("""'This is a quote'""", "This is a quote"),
            ('"This is a quote"', "This is a quote"),
            ("This is a quote", "This is a quote"),
        ]
        for case in cases:
            s, expected = case
            result = Utils.strip_quotes(s)
            self.assertNotEqual(result, None)
            self.assertEqual(result, expected)

    def test_tryYamlRead(self):
        pass

    def test_urlToFileSystemPath(self):
        """
        It should translate the URL to a path in the local filesystem.
        """
        cases = [
            ("http://www.example.com/path/to/file.jpg", "/srv/ha/example.com","/srv/ha/example.com/path/to/file.jpg"),
            ("http://www.example.com:8080/path/to/file.jpg", "/srv/ha/example.com","/srv/ha/example.com/path/to/file.jpg"),
            ("https://www.example.com/path/to/file.jpg", "/srv/ha/example.com","/srv/ha/example.com/path/to/file.jpg"),
            ("http://example.com/path/to/file.jpg", "/srv/ha/example.com/","/srv/ha/example.com/path/to/file.jpg"),
        ]
        for case in cases:
            url, root, path = case
            result = Utils.urlToFileSystemPath(url, root)
            self.assertNotEqual(result, None)
            self.assertEqual(path, result)

    def test_validate(self):
        pass

    def test_write(self):
        pass

    def test_writeYaml(self):
        pass
