"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from Indexer import Utils

import inspect
import logging
import os
import shutil
import tempfile
import unittest


class TestUtils(unittest.TestCase):
    pass

    def setUp(self):
        self.log = logging.getLogger()
        self.module = os.path.abspath(inspect.getfile(self.__class__))
        self.module_path = os.path.dirname(self.module)
        self.temp = tempfile.mkdtemp()
        self.tests = os.sep.join([self.module_path, "utils"])

    def tearDown(self):
        shutil.rmtree(self.temp)

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
            filename, expected = case
            result = Utils.getFileNameExtension(filename)
            self.assertEquals(expected, result)

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

    def test_getTemporaryFileFromResource(self):
        """
        It should retrieve the web or file system resource and write it to a
        temporary file on the local file system, then return the path to the
        temporary file. It should throw an exception if any step in the
        procedure fails.
        """
        cases = [
            ("http://www.findandconnect.gov.au/assets/img/footer-logo.png", True),
            ("http://www.findandconnect.gov.au/assets/img/by-nc-sa.png", True),
            ("http://www.example.com/missing-image.png", False),
        ]
        for case in cases:
            source, expected = case
            try:
                result = Utils.getTemporaryFileFromResource(source)
                self.assertEqual(os.path.exists(result), expected)
            except:
                self.assertEqual(False, expected)
                # logging.error("Could not create temporary resource", exc_info=True)

    def test_isDigitalObjectYaml(self):
        """
        It should determine if a file is in YAML format, and if it represents a
        digital object.
        """
        cases = [

        ]
        for case in cases:
            path, expected = case
            result = Utils.isDigitalObjectYaml(path)
            self.assertEquals(expected, result)

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
            url, expected = case
            result = Utils.isUrl(url)
            self.assertEquals(expected, result)

    def test_loadFileHashIndex(self):
        """
        It should load the file hash index from a YAML file.
        """
        source = self.tests + os.sep + "hash_index"
        cases = [
            (source + os.sep + "1", 3),
            (source + os.sep + "2", 4),
        ]
        for case in cases:
            path, expected = case
            hash_index = Utils.loadFileHashIndex(path)
            self.assertNotEqual(None, hash_index)
            self.assertEqual(expected, len(hash_index))

    def test_map_url_to_local_path(self):
        """
        It should return a local file system path, given the local file system
        path to the root of a web site and a web URL.
        """
        cases = [
            ("/var/www/TEST","http://www.example.com/image.jpg","/var/www/TEST/image.jpg"),
            ("/var/www/TEST","http://www.example.com/","/var/www/TEST"),
            ("/var/www/TEST","http://www.example.com/../","/var/www/TEST"),
            ("/var/www/TEST","http://www.example.com/path/to/subdirectory/","/var/www/TEST/path/to/subdirectory"),
            ("/var/www/TEST","http://www.example.com/path/to/subdirectory","/var/www/TEST/path/to/subdirectory"),
        ]
        for case in cases:
            site_path, resource_url, expected = case
            result = Utils.map_url_to_local_path(resource_url, site_path)
            self.assertNotEqual(result, None)
            self.assertEqual(result, expected)

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
        """
        It should recursively delete the contents of the specified folder.
        """
        cases = [
            (self.tests + os.sep + "purge", "1", [], 0),
            (self.tests + os.sep + "purge", "2", ['file1','file2'], 2),
            (self.tests + os.sep + "purge", "3", ['file0','file3'], 1),
        ]
        for case in cases:
            source_path, folder_name, keep_files, expected_count = case
            file_index = {}
            for f in keep_files:
                file_index[f] = "file hash"
            source = source_path + os.sep + folder_name
            dest = self.temp + os.sep + folder_name
            try:
                shutil.copytree(source, dest)
            except:
                msg = "Could not copy testing files {0} to temp folder {1}".format(source, dest)
                self.fail(msg)
            try:
                Utils.purgeFolder(dest, file_index)
            except:
                msg = "Could not purge folder {}".format(self.temp)
                self.log.error(msg, exc_info=True)
                self.fail(msg)
            # the file count should be equal to expected
            files = os.listdir(dest)
            self.assertEqual(expected_count, len(files))

    def test_purgeIndex(self):
        """
        It should remove all entries in the index that are not represented in
        the file list.
        """
        cases = [
            (['ABC','DEF'],{"ABC":"hash","DEF":"hash","GHI":"hash"}, 2),
        ]
        for case in cases:
            records, index, expected = case
            index = Utils.purgeIndex(records, index)
            self.assertNotEqual(None, index)
            self.assertEqual(expected, len(index))

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

    def test_writeFileHashIndex(self):
        """
        It should write a file hash index in YAML format.
        """
        cases = []
        for case in cases:
            data, expected = case

    def test_writeYaml(self):
        pass
