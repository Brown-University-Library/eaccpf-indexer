"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

import unittest


class TestDigitalObject(unittest.TestCase):
    """
    Unit tests for DigitalObject module.
    """

    def setUp(self):
        """
        Setup the test environment.
        """
        pass

    def tearDown(self):
        """
        Tear down the test environment.
        """
        pass

    def test__getDateRange(self):
        """
        It should parse a unitdate and produce valid fromDate and toDate 
        values.
        """
        cases = {
                 }
        for case in cases:
            print case

    def test__getType(self):
        """
        It should determine whether a resource specified by a URL is one of 
        image, video or other.
        """
        cases = {
                 "http://www.findandconnect.gov.au/nsw/eac/NE01217.xml":"other",
                 "http://www.findandconnect.gov.au/nsw/site/images/logo-nsw.png":"image",
                 "http://www.findandconnect.gov.au/nsw/objects/thumbs/tn_Mowbray%20Park.png":"image",
                 "http://www.findandconnect.gov.au/nsw/site/images/external-link.gif":"image",
                 }
        for case in cases:
            # datatype = doc._getDigitalObjectType(case)
            # self.assertEquals(datatype,cases[case])
            print case

if __name__ == "__main__":
    unittest.main()
