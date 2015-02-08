#!/usr/bin/python

import unittest

from loc import gmaps_api
import locations

class TestCityNames(unittest.TestCase):
    def runTest(self):
        self.assertEqual(locations.get_geocoded_name(gmaps_api.get_geocode(address='San Francisco, CA')), u'San Francisco, CA, US')
        self.assertEqual(locations.get_geocoded_name(gmaps_api.get_geocode(address='Tokyo, Japan')), u'Tokyo, Japan')
        self.assertEqual(locations.get_geocoded_name(gmaps_api.get_geocode(address='Osaka')), u'Osaka, Osaka Prefecture, Japan')
        self.assertEqual(locations.get_geocoded_name(gmaps_api.get_geocode(address='Mexico City, Mexico')), u'Mexico City, DF, Mexico')
