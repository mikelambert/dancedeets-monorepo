# -*-*- encoding: utf-8 -*-*-

import unittest

from loc import gmaps_api
from loc import gmaps_local
from loc import formatting


formatting_reg_data = {
    'Shibuya': 'Shibuya, Tokyo, Japan',
    u'渋谷': 'Shibuya, Tokyo, Japan',
    'Ginza': 'Ginza, Chuo, Tokyo, Japan',
    'Osaka': 'Osaka, Osaka Prefecture, Japan',
    'Nagoya': 'Nagoya, Aichi Prefecture, Japan',
    'Kowloon': 'Kowloon, Hong Kong',
    'Hong Kong Island': 'Hong Kong Island, Hong Kong',
    'Shanghai': 'Shanghai, China',
    'Sao Paulo, Brazil': u'S\xe3o Paulo, Brazil',
    'Taipei': 'Taipei, Taiwan',
    'Miami, FL': 'Miami, FL, United States',
    'Sydney': 'Sydney, NSW, Australia',
    'Paris': 'Paris, France',
    'London': 'London, United Kingdom',
    'Helsinki': 'Helsinki, Finland',
    'Bay Area': 'San Francisco Bay Area, CA, United States',
    'Brooklyn': 'Brooklyn, New York, NY, United States',
    'Williamsburg, Brooklyn': 'Williamsburg, Brooklyn, New York, NY, United States',
    'SOMA, SF, CA': 'South of Market, San Francisco, CA, United States',
    '6 5th Street, SF, CA': 'South of Market, San Francisco, CA, United States',
    'Irvine': 'Irvine, CA, United States',
    'New England': 'New England',
    'The Haight': 'Haight-Ashbury, San Francisco, CA, United States',
    'Europe': 'Europe',
    'Asia': 'Asia',
    'Mexico City': 'Mexico City, DF, Mexico',
}


class GmapsTestCase(unittest.TestCase):
    def setUp(self):
        self.original_backend = gmaps_api.gmaps_backend
        gmaps_api.gmaps_backend = gmaps_local

    def tearDown(self):
        gmaps_api.gmaps_backend = self.original_backend

class TestLocationFormatting(GmapsTestCase):
    def runTest(self):
        for address, final_address in formatting_reg_data.iteritems():
            formatted_address = formatting.format_geocode(gmaps_api.get_geocode(address=address), include_neighborhood=True)
            if formatted_address != final_address:
                print 'formatted address for %r is %r, should be %r' % (address, formatted_address, final_address)
                print gmaps_local.fetch_raw(address=address)
                self.assertEqual(final_address, formatted_address)

grouping_lists = [
    (['Miami, FL', 'Soma, SF, CA', 'Williamsburg, Brooklyn'], ['Miami, FL', 'South of Market, San Francisco, CA', 'Brooklyn, New York, NY']),
    (['Brooklyn', 'Williamsburg, Brooklyn'], ['Brooklyn', 'Williamsburg, Brooklyn']),
    (['SOMA, SF, CA', '6 5th Street, SF, CA'], ['South of Market', 'South of Market']),
    (['Bay Area', '6 5th Street, SF, CA'], ['San Francisco Bay Area, CA', 'South of Market, San Francisco, CA']),
    (['Shibuya', 'Ginza'], ['Shibuya, Tokyo', 'Ginza, Chuo, Tokyo']),
    (['Shibuya', 'Ginza', 'Osaka'], ['Shibuya, Tokyo', 'Ginza, Chuo, Tokyo', 'Osaka, Osaka Prefecture']),
    (['Nagoya', 'Sydney'], ['Nagoya, Aichi Prefecture, Japan', 'Sydney, NSW, Australia']),
]

class TestMultiLocationFormatting(GmapsTestCase):
    def runTest(self):
        for addresses, reformatted_addresses in grouping_lists:
            geocodes = [gmaps_api.get_geocode(address=address) for address in addresses]
            reformatted_parts = formatting.format_geocodes(geocodes, include_neighborhood=True)
            self.assertEqual(reformatted_parts, reformatted_addresses)


if __name__ == '__main__':
    TestLocationFormatting().runTest()
    TestMultiLocationFormatting().runTest()
