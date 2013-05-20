"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

import HtmlPage
import os
import unittest

class HtmlPageUnitTests(unittest.TestCase):
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
        cases = {
                 "http://www.findandconnect.gov.au/nsw/" : False,                       # region home case
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00200b.htm" : True,      # organization case
                 "http://www.findandconnect.gov.au/nsw/objects/ND0000021.htm" : False   # digital object
                 }
        for case in cases:
            html = HtmlPage.HtmlPage(case)
            result = html.hasEacCpfAlternate()
            self.assertEqual(result, cases[case])
    
    def test_getDocumentParentUrl(self):
        """
        It should return the URL of the first parent directory where a file is
        reference, and the directory itself where a directory is referenced.
        """
        cases = {
                 "http://www.findandconnect.gov.au/nsw/" : "http://www.findandconnect.gov.au/nsw/",                         
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00200b.htm" : "http://www.findandconnect.gov.au/nsw/biogs/", 
                 "http://www.findandconnect.gov.au/nsw/objects/ND0000021.htm" : "http://www.findandconnect.gov.au/nsw/objects/"
                 }
        for case in cases:
            html = HtmlPage.HtmlPage(case)
            result = html._getDocumentParentUri(case)
            self.assertEqual(result, cases[case])
    
    def test_getDocumentUrl(self):
        """
        It should return the document URI.
        @todo this is not functioning correctly for the case where a base url is provided!!!
        """
        cases = [
                 "http://www.findandconnect.gov.au/nsw/index.php",
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00200b.htm",
                 "http://www.findandconnect.gov.au/nsw/objects/ND0000021.htm",
                 "http://www.findandconnect.gov.au/vic/feedback.html",
                 ]
        for case in cases:
            html = HtmlPage.HtmlPage(case)
            result = html.getUrl()
            self.assertEqual(result, case)
            # the url should not have any spaces in it
            self.assertEqual(result.count(' '), 0)
        # path to the test data folder
        parentpath = self._getParentPath(HtmlPage.__file__)
        if not parentpath.endswith('/'):
            parentpath = parentpath + '/'
        path = parentpath + 'test' + os.sep + 'html'
        # test cases for where a base url is provided
        bases = [
                 "http://www.example.com",
                 "http://www.example.com/",
                 "http://www.example.com/path",
                 "http://www.example.com/path/",
                 ]
        files = os.listdir(path)
        for base in bases:
            if not base.endswith('/'):
                myurl = base + '/'
            for filename in files:
                html = HtmlPage.HtmlPage(path + os.sep + filename, base)
                url = html.getUrl()
                fn = html.getFilename()
                self.assertEqual(url, myurl + fn)

    def test_getRecordId(self):
        """
        It should return a record id for cases that represent a digital object
        or that have an EAC-CPF alternate representation.
        """
        cases = {
                 "http://www.findandconnect.gov.au/nsw/" : None,                            # region home case
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00200b.htm" : "NE00200b",    # organization case
                 "http://www.findandconnect.gov.au/nsw/objects/ND0000171.htm" : "ND0000171",# image
                 "http://www.findandconnect.gov.au/vic/objects/D00000342.htm" : "D00000342",# VIDEO digital object
                 "http://www.findandconnect.gov.au/nsw/browse_h.htm": None,                 # browse case
                 }
        for case in cases:
            html = HtmlPage.HtmlPage(case)
            result = html.getRecordId()
            if result:
                self.assertEqual(result,cases[case])
            
if __name__ == '__main__':
    unittest.main()

    