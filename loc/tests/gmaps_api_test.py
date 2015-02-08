import unittest

from loc import gmaps_api

class TestGetCountry(unittest.TestCase):
    def runTest(self):
        self.assertEqual(gmaps_api.get_geocode(address='San Francisco').country(), u'US')
        self.assertEqual(gmaps_api.get_geocode(address='Tokyo').country(), u'JP')
