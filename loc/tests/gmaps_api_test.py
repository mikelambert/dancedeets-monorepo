import unittest

from loc import gmaps_api

class TestGetCountry(unittest.TestCase):
    def setUp(self):
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def runTest(self):
        self.assertEqual(gmaps_api.get_geocode(address='San Francisco').country(), u'US')
        self.assertEqual(gmaps_api.get_geocode(address='Tokyo').country(), u'JP')
