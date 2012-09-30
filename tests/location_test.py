#!/usr/bin/python

import unittest

import locations

class TestLocations(unittest.TestCase):
    def test_get_city_name(self):
        self.assertEqual(locations.get_city_name(address='San Francisco, CA'), u'San Francisco, CA, US')
        self.assertEqual(locations.get_city_name(address='Tokyo, Japan'), u'Tokyo, Japan')
        self.assertEqual(locations.get_city_name(address='Osaka'), u'Osaka, Osaka Prefecture, Japan')
        self.assertEqual(locations.get_city_name(address='Mexico City, Mexico'), u'Mexico City, D.F., Mexico')

    def test_get_country(self):
        self.assertEqual(locations.get_country_for_location('San Francisco'), u'US')
        self.assertEqual(locations.get_country_for_location('Tokyo'), u'JP')
