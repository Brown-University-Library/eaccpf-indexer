'''
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
'''

import unittest
import HtmlPage

class HtmlPageUnitTests(unittest.TestCase):
    '''
    Test cases for the HTML Page module.
    @todo Need test cases for when the page contains relative URLs throughout
    '''
    
    def setUp(self):
        '''
        Setup the test environment.
        '''
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
        '''
        Tear down the test environment.
        '''
        pass

    def test_init(self):
        '''
        It should create an object instance, and the specified page content 
        should be loaded if it exists.
        '''
        # create a list of pages to load and test
        pages = [
                 "http://www.findandconnect.gov.au/nsw/",                       # region home page
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00200b.htm",     # organization page
                 "http://www.findandconnect.gov.au/nsw/objects/ND0000021.htm"   # digital object
                 ]
        for page in pages:
            html = HtmlPage.HtmlPage(page)
            url = html.source
            data = html.data
            self.assertNotEqual(html, None)
            self.assertEqual(page,url)
            self.assertNotEqual(data, None)
    
    def test_hasDigitalObject(self):
        '''
        It should return true if a digital object properties table is present  
        within the HTML. If a digital object properties table is not present it 
        should return a negative result.
        '''
        pages = {
                 "http://www.findandconnect.gov.au/nsw/" : False,                       # region home page
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00200b.htm" : False,     # organization page
                 "http://www.findandconnect.gov.au/nsw/objects/ND0000021.htm" : True,   # digital object
                 "http://www.findandconnect.gov.au/nsw/browse_h.htm" : False,           # browse page
                 }
        for page in pages:
            html = HtmlPage.HtmlPage(page)
            result = html.hasDigitalObject()
            self.assertEqual(result, pages[page])
    
    def test_hasEacCpfAlternate(self):
        '''
        It should return true if there is an EAC-CPF alternate representation 
        specified for the HTML page. It should return false if none is 
        specified. 
        '''
        pages = {
                 "http://www.findandconnect.gov.au/nsw/" : False,                       # region home page
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00200b.htm" : True,      # organization page
                 "http://www.findandconnect.gov.au/nsw/objects/ND0000021.htm" : False   # digital object
                 }
        for page in pages:
            html = HtmlPage.HtmlPage(page)
            result = html.hasEacCpfAlternate()
            self.assertEqual(result, pages[page])
    
    def test_getDigitalObject(self):
        '''
        It should return a digital object record with the minimum required 
        fields.
        '''
        pages = {
                 "http://www.findandconnect.gov.au/nsw/" : False,                       # region home page
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00200b.htm" : False,     # organization page
                 "http://www.findandconnect.gov.au/nsw/objects/ND0000171.htm" : True,   # image
                 "http://www.findandconnect.gov.au/vic/objects/D00000342.htm" : False,  # video digital object
                 "http://www.findandconnect.gov.au/vic/objects/D00000277.htm" : True,   # image
                 "http://www.findandconnect.gov.au/wa/objects/WD0000233.htm" : True,    # image
                 "http://www.findandconnect.gov.au/nsw/browse_h.htm": False,            # browse page
                 }
        for page in pages:
            html = HtmlPage.HtmlPage(page)
            result = html.getDigitalObject()
            self.assertNotEqual(result,pages[page])
            # the digital object must have a url property at minimum
            if result:
                self.assertIn("url",result)  
                self.assertNotEqual(result['url'],None)
    
    def test_getDocumentParentUri(self):
        '''
        It should return the URL of the first parent directory where a file is
        reference, and the directory itself where a directory is referenced.
        '''
        pages = {
                 "http://www.findandconnect.gov.au/nsw/" : "http://www.findandconnect.gov.au/nsw/",                         
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00200b.htm" : "http://www.findandconnect.gov.au/nsw/biogs/", 
                 "http://www.findandconnect.gov.au/nsw/objects/ND0000021.htm" : "http://www.findandconnect.gov.au/nsw/objects/"
                 }
        for page in pages:
            html = HtmlPage.HtmlPage(page)
            result = html._getDocumentParentUri(page)
            self.assertEqual(result, pages[page])
    
    def test_getRecordId(self):
        '''
        It should return a record id for pages that represent a digital object
        or that have an EAC-CPF alternate representation.
        '''
        pages = {
                 "http://www.findandconnect.gov.au/nsw/" : None,                            # region home page
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00200b.htm" : "NE00200b",    # organization page
                 "http://www.findandconnect.gov.au/nsw/objects/ND0000171.htm" : "ND0000171",# image
                 "http://www.findandconnect.gov.au/vic/objects/D00000342.htm" : "D00000342",# VIDEO digital object
                 "http://www.findandconnect.gov.au/nsw/browse_h.htm": None,                 # browse page
                 }
        for page in pages:
            html = HtmlPage.HtmlPage(page)
            result = html.getRecordId()
            if result:
                self.assertEqual(result,pages[page])

    def test_getUri(self):
        '''
        It should return the document URI.
        '''
        pages = [
                 "http://www.findandconnect.gov.au/nsw/index.php",
                 "http://www.findandconnect.gov.au/nsw/biogs/NE00200b.htm",
                 "http://www.findandconnect.gov.au/nsw/objects/ND0000021.htm",
                 "http://www.findandconnect.gov.au/vic/feedback.html",
                 ]
        for page in pages:
            html = HtmlPage.HtmlPage(page)
            result = html.getUri()
            self.assertEqual(result, page)
            # the url should not have any spaces in it
            self.assertEqual(result.count(' '), 0)
            
if __name__ == '__main__':
    unittest.main()

    