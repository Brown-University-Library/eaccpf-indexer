"""
This file is subject to the terms and conditions defined in the
LICENSE file, which is part of this source code package.
"""

from .. import Facter

import unittest


class TestFacter(unittest.TestCase):
    """
    Unit tests for Facter module.
    """

    def setUp(self):
        """
        Setup the test environment.
        """
        self.facter = Facter.Facter()

    def tearDown(self):
        """
        Tear down the test environment.
        """
        pass

    def test__init__(self):
        """
        It should return an instance of the class.
        """
        self.assertNotEqual(self.facter,None)

    def test__addValueToDictionary(self):
        pass

    def test__getAddressParts(self):
        """
        It should return the components of the address string.
        """
        cases = {
                 "Rapid Creek NT, Australia" : ['',"Rapid Creek","NT",'',"Australia"],
                 "Mulgowie QLD 4341, Australia" : ['',"Mulgowie","QLD","4341","Australia"],
                 "Brinsley Road, Camberwell VIC 3124, Australia" : ["Brinsley Road","Camberwell","VIC","3124","Australia"],
                 "Boys Home Road, Phillip Island VIC 3925, Australia" : ["Boys Home Road","Phillip Island","VIC","3925","Australia"],
                 "William Road, Carrum Downs VIC 3201, Australia" : ["William Road","Carrum Downs","VIC","3201","Australia"],
                 "Lawson, University of Southern Queensland Education City Drive, Springfield Central QLD 4300, Australia" : ["Lawson, University of Southern Queensland Education City Drive","Springfield Central","QLD","4300","Australia"],
                 "Gore Hill, Montana 59404, USA" : ['',"Gore Hill","Montana","59404","USA"],
                 "Gore Hill, Amersham, Buckinghamshire HP7, UK" : ["Gore Hill","Amersham","Buckinghamshire","HP7","UK"],
                 "Gore Hill, Sandford, Wareham, Dorset BH20 7AL, UK" : ["Gore Hill, Sandford","Wareham","Dorset","BH20 7AL","UK"],
                 }
        for case in cases:
            address,city,region,postal,country = self.facter._getAddressParts(case)
            self.assertEqual(address,cases[case][0])
            self.assertEqual(city,cases[case][1])
            self.assertEqual(region,cases[case][2])
            self.assertEqual(postal,cases[case][3])
            self.assertEqual(country,cases[case][4])

    def test__getCalaisResultAsDictionary(self):
        """
        """
        pass

    def test_inferEntitiesWithAlchemy(self):
        """
        """
        pass

    def test_inferEntitiesWithCalais(self):
        """
        """
        pass

    def test_inferEntitiesWithNLTK(self):
        """
        """
        pass

    def test_infer(self):
        """
        """
        pass

    def test_inferLocations(self):
        """
        It should infer
        """
        pass


if __name__ == "__main__":
    unittest.main()
