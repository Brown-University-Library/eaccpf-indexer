"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from Indexer import HtmlPage

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
        self.module_path = os.path.dirname(module)
        self.log = logging.getLogger()
        self.test_html = os.sep.join([self.module_path, "html"])
        self.test_site = os.sep.join([self.module_path, "test_site"])
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
            (self.test_site, "browse.htm"),
            (self.test_site + os.sep + "biogs", "NE00500b.htm"),
            (self.test_site + os.sep + "biogs", "NE00001b.htm"),
            (self.test_site + os.sep + "objects", "ND0000001.htm"),
         ]
        for case in cases:
            path, filename = case
            html = HtmlPage.HtmlPage(path, filename=filename)
            self.assertNotEqual(None, html)

    def test_hasEacCpfAlternate(self):
        """
        It should return true if there is an EAC-CPF alternate representation 
        specified for the HTML case. It should return false if none is 
        specified. 
        """
        cases = [
            (self.test_site, "browse.htm", False),
            (self.test_site + os.sep + "biogs", "NE00500b.htm", True),
            (self.test_site + os.sep + "biogs", "NE00001b.htm", True),
            (self.test_site + os.sep + "objects", "ND0000001.htm", False),
        ]
        for case in cases:
            path, filename, expected = case
            html = HtmlPage.HtmlPage(path, filename=filename)
            result = html.hasEacCpfAlternate()
            self.assertNotEqual(None, result)
            self.assertEqual(expected, result)

    def test_getContent(self):
        """
        It should return the HTML content.
        """
        cases = [
            (self.test_site + os.sep + "objects", "ND0000001.htm"),
            (self.test_site + os.sep + "biogs", "NE00001b.htm"),
        ]
        for case in cases:
            path, filename = case
            html = HtmlPage.HtmlPage(path, filename=filename)
            self.assertNotEqual(None, html)
            result = html.getContent()
            self.assertNotEqual(None, result)
            self.assertLess(0, result)

    def test_getRecordId(self):
        """
        It should return a record id for documents that represent an entity.
        """
        cases = [
            (self.test_site + os.sep + "biogs", "NE00200b.htm", "NE00200b"),
            (self.test_site + os.sep + "objects", "ND0000171.htm", None),
            (self.test_site, "browse.htm", None)
        ]
        for case in cases:
            path, filename, expected = case
            html = HtmlPage.HtmlPage(path, filename=filename)
            result = html.getRecordId()
            self.assertEqual(expected, result)

    def test_getText(self):
        """
        It should return the BODY text with tags, comments and all Javascript
        removed.
        """
        cases = [
            (self.test_html, "javascript_and_comments_in_body_1.html"),
            (self.test_html, "javascript_and_comments_in_body_2.html"),
        ]
        for case in cases:
            path, filename = case
            html = HtmlPage.HtmlPage(path, filename=filename)
            text = html.getText()
            has_comment = True if '<!-- ' in text or '-->' in text else False
            self.assertEqual(False, has_comment)
            j1 = "document.createElement('script');"
            j2 = "encodeURIComponent($(this).attr('title'));"
            has_javascript = True if j1 in text or j2 in text else False
            self.assertEqual(False, has_javascript)

    def test_getTitle(self):
        """
        It should return the title value from the document HEAD. For titles
        with markup, the markup should be removed. See issue #30.
        """
        cases = [
            (self.test_html, 'markup_in_title_1.htm',"Anglicare Victoria - Organisation - Find & Connect - Victoria"),
            (self.test_html, 'markup_in_title_2.htm',"Anglicare Victoria - Organisation - Find & Connect - Victoria"),
            (self.test_html, 'markup_in_title_3.htm',"Anglicare Victoria - Organisation - Find & Connect - Victoria"),
            (self.test_html, 'markup_in_title_4.htm',"Anglicare Victoria (1978/1) - Organisation - Find & Connect - Victoria"),
            (self.test_html, 'markup_in_title_5.htm',"Anglicare Victoria (1978/1) - Organisation - Find & Connect - Victoria"),
        ]
        for case in cases:
            path, filename, expected = case
            doc = HtmlPage.HtmlPage(path, filename=filename)
            self.assertNotEqual(None, doc)
            result = doc.getTitle()
            self.assertEqual(expected, result)

    def test_getUrl(self):
        """
        It should return the public document URL.
        """
        cases = [
            (self.test_site + os.sep + "biogs", "NE00001b.htm", "http://www.findandconnect.gov.au/nsw/biogs/NE00001b.htm"),
            (self.test_site + os.sep + "objects", "ND0000005.htm", "http://www.findandconnect.gov.au/nsw/objects/ND0000005.htm"),
            (self.test_site, "browse.htm", "http://www.findandconnect.gov.au/nsw/browse.htm"),
        ]
        for case in cases:
            path, filename, expected = case
            html = HtmlPage.HtmlPage(path, filename=filename)
            result = html.getUrl()
            self.assertEqual(expected, result)

    def test_getUrl_with_base(self):
        """
        It should return the public document URL. In this case we provide a
        base URL value, which will override the embedded document URL value.
        """
        cases = [
            (self.test_html, "E000001b.htm", "http://www.example.com",  "http://www.example.com/E000001b.htm"),
            (self.test_html, "E000001b.htm", "http://www.example.com/", "http://www.example.com/E000001b.htm"),
            (self.test_html, "E000001b.htm", "http://www.example.com/path",  "http://www.example.com/path/E000001b.htm"),
            (self.test_html, "E000001b.htm", "http://www.example.com/path/", "http://www.example.com/path/E000001b.htm"),
            (self.test_html, "E000001b.htm", "http://www.example.com/path/to",  "http://www.example.com/path/to/E000001b.htm"),
            (self.test_html, "E000001b.htm", "http://www.example.com/path/to/", "http://www.example.com/path/to/E000001b.htm"),
        ]
        for case in cases:
            path, filename, base, expected = case
            html = HtmlPage.HtmlPage(path, filename=filename, base_url=base)
            url = html.getUrl()
            self.assertEqual(expected, url)


if __name__ == '__main__':
    unittest.main()

