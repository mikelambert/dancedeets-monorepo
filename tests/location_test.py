#!/usr/bin/python

import unittest

import locations

class TestCityNames(unittest.TestCase):
    def runTest(self):
        self.assertEqual(locations.get_name(address='San Francisco, CA'), u'San Francisco, CA, US')
        self.assertEqual(locations.get_name(address='Tokyo, Japan'), u'Tokyo, Japan')
        self.assertEqual(locations.get_name(address='Osaka'), u'Osaka, Osaka Prefecture, Japan')
        self.assertEqual(locations.get_name(address='Mexico City, Mexico'), u'Mexico City, D.F., Mexico')


class TestGetCountry(unittest.TestCase):
    def runTest(self):
        self.assertEqual(locations.get_country_for_location('San Francisco'), u'US')
        self.assertEqual(locations.get_country_for_location('Tokyo'), u'JP')
