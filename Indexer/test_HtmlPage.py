"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

import HtmlPage
import inspect
import logging
import os
import unittest


class TestHtmlPage(unittest.TestCase):
    """
    Test cases for the HTML Page module.
    @todo Need test cases for when the page contains relative URLs throughout
    """
    def _getParentPath(self, Path):
        """
        Get the path to the parent of the specified directory.
        """
        i = Path.rfind('/')
        return Path[:i+1]
    
    def setUp(self):
        """
        Setup the test environment.
        """
        module = os.path.abspath(inspect.getfile(self.__class__))
        module_path = os.path.dirname(module)
        self.log = logging.getLogger()
        self.test_html = os.sep.join([module_path, "test", "html", os.sep])
        self.test_site = os.sep.join([module_path, "test", "test_site", os.sep])
        self.html = """<html>
            <head>
                <title>TEST</title>
                <meta name="DC.Title" lang="en" content="TEST" />
                <meta name="DC.Creator" lang="en" content="TEST" />
                <meta name="DC.Subject" lang="en" content="TEST" />
                <meta name="DC.Description" lang="en" content="TEST" />
                <meta name="DC.Publisher" lang="en" content="TEST" />
                <meta name="DC.Date.Created" scheme="ISO8601" lang="en" content="2013-01-01" />
                <meta name="DC.Date.LastModified" scheme="ISO8601" lang="en" content="2013-01-01" />
                <meta name="DC.Type" lang="en" content="TEST" />
                <meta name="DC.Format" scheme="IMT" lang="en" content="text/html" />
                <meta name="DC.Identifier" scheme="URL" lang="en" content="http://www.example.com/path/to/file.htm" />
                <meta name="DC.Language" scheme="ISO639" lang="en" content="en-gb" />
                <meta name="DC.Rights" lang="en" content="TEST" />
                <meta name="Author" lang="en" content="TEST" />
                <meta name="Description" lang="en" content="TEST" />
                <meta name="Keywords" lang="en" content="TEST" />
            </head>
            <body>
                TEST
            </body>
        </html>
        """
        self.htmldigitalobject = """<html>
            <head>
                <title>Image - TEST</title>
                <meta name="DC.Title" lang="en" content="TEST" />
                <meta name="DC.Creator" lang="en" content="TEST" />
                <meta name="DC.Subject" lang="en" content="TEST" />
                <meta name="DC.Description" lang="en" content="TEST" />
                <meta name="DC.Publisher" lang="en" content="TEST" />
                <meta name="DC.Date.Created" scheme="ISO8601" lang="en" content="2013-01-01" />
                <meta name="DC.Date.LastModified" scheme="ISO8601" lang="en" content="2013-01-01" />
                <meta name="DC.Type" lang="en" content="TEST" />
                <meta name="DC.Format" scheme="IMT" lang="en" content="text/html" />
                <meta name="DC.Identifier" scheme="URL" lang="en" content="http://www.example.com/path/to/file.htm" />
                <meta name="DC.Language" scheme="ISO639" lang="en" content="en-gb" />
                <meta name="DC.Rights" lang="en" content="TEST" />
                <meta name="Author" lang="en" content="TEST" />
                <meta name="Description" lang="en" content="TEST" />
                <meta name="Keywords" lang="en" content="TEST" />
            </head>
            <body>
                TEST
            </body>
        </html>
        """
        self.htmleaccpf = """<html>
            <head>
                <title>TEST</title>
                <meta name="DC.Title" lang="en" content="TEST" />
                <meta name="DC.Creator" lang="en" content="TEST" />
                <meta name="DC.Subject" lang="en" content="TEST" />
                <meta name="DC.Description" lang="en" content="TEST" />
                <meta name="DC.Publisher" lang="en" content="TEST" />
                <meta name="DC.Date.Created" scheme="ISO8601" lang="en" content="2013-01-01" />
                <meta name="DC.Date.LastModified" scheme="ISO8601" lang="en" content="2013-01-01" />
                <meta name="DC.Type" lang="en" content="TEST" />
                <meta name="DC.Format" scheme="IMT" lang="en" content="text/html" />
                <meta name="DC.Identifier" scheme="URL" lang="en" content="http://www.example.com/path/to/file.htm" />
                <meta name="DC.Language" scheme="ISO639" lang="en" content="en-gb" />
                <meta name="DC.Rights" lang="en" content="TEST" />
                <meta name="Author" lang="en" content="TEST" />
                <meta name="Description" lang="en" content="TEST" />
                <meta name="Keywords" lang="en" content="TEST" />
                <meta name="EAC" lang="en" content="http://www.example.com/path/to/file.htm" />
            </head>
            <body>
                TEST
            </body>
        </html>
        """

    def tearDown(self):
        """
        Tear down the test environment.
        """
        pass

    def test_init(self):
        """
        It should create an object instance, and the specified case content 
        should be loaded if it exists.
        """
        # create a list of cases to load and test
        cases = [
                 "http://www.findandconnect.gov.au/nsw/",                       # region home case
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00200b.htm",     # organization case
                 "http://www.findandconnect.gov.au/nsw/objects/ND0000021.htm"   # digital object
                 ]
        for case in cases:
            html = HtmlPage.HtmlPage(case)
            url = html.source
            data = html.data
            self.assertNotEqual(html, None)
            self.assertEqual(case,url)
            self.assertNotEqual(data, None)
    
    def test_hasEacCpfAlternate(self):
        """
        It should return true if there is an EAC-CPF alternate representation 
        specified for the HTML case. It should return false if none is 
        specified. 
        """
        cases = [
            (self.test_site + "browse.htm", False),
            (self.test_site + "biogs" + os.sep + "NE00500b.htm", True),
            (self.test_site + "biogs" + os.sep + "NE00001b.htm", True),
            (self.test_site + "objects" + os.sep + "ND0000001.htm", False),
        ]
        for case in cases:
            source, expected = case
            html = HtmlPage.HtmlPage(source)
            result = html.hasEacCpfAlternate()
            self.assertNotEqual(None, result)
            self.assertEqual(expected, result)

    def test_getContent(self):
        """
        It should return the HTML content.
        """
        cases = [
            self.test_site + "objects" + os.sep + "ND0000001.htm",
            self.test_site + "biogs" + os.sep + "NE00001b.htm",
        ]
        for case in cases:
            html = HtmlPage.HtmlPage(case)
            self.assertNotEqual(None, html)
            result = html.getContent()
            self.assertNotEqual(None, result)
            self.assertLess(0, result)

    def test_getDocumentUrl(self):
        """
        It should return the HTML document URL.
        @todo this is not functioning correctly for the case where a base url is provided!!!
        """
        cases = [
            (self.test_site + "biogs" + os.sep + "NE00001b.htm", "http://www.findandconnect.gov.au/nsw/biogs/NE00001b.htm"),
            (self.test_site + "objects" + os.sep + "ND0000005.htm", "http://www.findandconnect.gov.au/nsw/objects/ND0000005.htm"),
            (self.test_site + "browse.htm", "http://www.findandconnect.gov.au/nsw/browse.htm"),
        ]
        for case in cases:
            source, expected = case
            html = HtmlPage.HtmlPage(source)
            result = html.getUrl()
            self.assertEqual(expected, result)

    def test_getDocumentUrl_with_base(self):
        """
        test cases for where a base url is provided
        """
        cases = [
            (self.test_html + "E000001b.htm","http://www.example.com","http://www.example.com/vic/biogs/E000001b.htm"),
            (self.test_html + "E000001b.htm","http://www.example.com/","http://www.example.com/vic/biogs/E000001b.htm"),
            (self.test_html + "E000001b.htm","http://www.example.com/path","http://www.example.com/path/vic/biogs/E000001b.htm"),
            (self.test_html + "E000001b.htm","http://www.example.com/path/","http://www.example.com/path/vic/biogs/E000001b.htm"),
        ]
        for case in cases:
            source, base, expected = case
            html = HtmlPage.HtmlPage(source, base)
            url = html.getUrl()
            self.assertEqual(expected, url)

    def test_getRecordId(self):
        """
        It should return a record id for cases that represent an entity.
        """
        cases = [
            (self.test_site + "biogs" + os.sep + "NE00200b.htm", "NE00200b"),
            (self.test_site + "objects" + os.sep + "ND0000171.htm", None),
            (self.test_site + "browse.htm", None)
        ]
        for case in cases:
            source, expected = case
            html = HtmlPage.HtmlPage(source)
            result = html.getRecordId()
            self.assertEqual(expected, result)

    def test_getTitle(self):
        """
        It should return the title value from the document HEAD. For titles
        with markup, the markup should be removed. See issue #30.
        """
        cases = [
            (self.test_html + 'markup_in_title_1.htm',"Anglicare Victoria - Organisation - Find & Connect - Victoria"),
            (self.test_html + 'markup_in_title_2.htm',"Anglicare Victoria - Organisation - Find & Connect - Victoria"),
            (self.test_html + 'markup_in_title_3.htm',"Anglicare Victoria - Organisation - Find & Connect - Victoria"),
            (self.test_html + 'markup_in_title_4.htm',"Anglicare Victoria (1978/1) - Organisation - Find & Connect - Victoria"),
            (self.test_html + 'markup_in_title_5.htm',"Anglicare Victoria (1978/1) - Organisation - Find & Connect - Victoria"),
        ]
        for case in cases:
            source, expected = case
            doc = HtmlPage.HtmlPage(source)
            self.assertNotEqual(None, doc)
            result = doc.getTitle()
            self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()

    