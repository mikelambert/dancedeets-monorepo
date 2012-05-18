#!/usr/bin/python

import unittest

import locations

class LocationsTest(unittest.TestCase):
    def test_geocoded_location(self):
        result = locations.get_geocoded_location(address='San Francisco, CA')
        self.assertEqual(result['city'], u'San Francisco, CA, US')

        result = locations.get_geocoded_location(address='Tokyo, Japan')
        self.assertEqual(result['city'], u'Tokyo, Japan')

        result = locations.get_geocoded_location(address='Mexico City, Mexico')
        self.assertEqual(result['city'], u'Mexico City, DF, Mexico')

if __name__ == '__main__':
    unittest.main()
