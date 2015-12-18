# -*-*- encoding: utf-8 -*-*-

import logging
import unittest

from loc import gmaps_api
from loc import gmaps_stub
from loc import formatting


formatting_reg_data = {
    'Shibuya': 'Shibuya, Tokyo, Japan',
    u'渋谷': 'Shibuya, Tokyo, Japan',
    'Ginza': u'Ginza, Chūō, Tokyo, Japan',
    'Osaka': 'Osaka, Osaka Prefecture, Japan',
    'Nagoya': 'Nagoya, Aichi Prefecture, Japan',
    'Kowloon': 'Kowloon, Hong Kong',
    'Hong Kong Island': 'Hong Kong Island, Hong Kong',
    'Shanghai': 'Shanghai, China',
    'Sao Paulo, Brazil': u'S\xe3o Paulo, Brazil',
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
    'Mexico City': 'Mexico City, D.F., Mexico',
    'Taipei, Taiwan 103': 'Taipei City, Taiwan',
    'Keelung, Taiwan 20241': 'Keelung City, Taiwan',
    'Taipei': 'Taipei, Taiwan',
    'Tangerang': 'Tangerang, Banten, Indonesia',
}


class GmapsTestCase(unittest.TestCase):
    def setUp(self):
        self.gmaps_stub = gmaps_stub.Stub()
        self.gmaps_stub.activate()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.gmaps_stub.deactivate()

class TestLocationFormatting(GmapsTestCase):
    def runTest(self):
        for address, final_address in formatting_reg_data.iteritems():
            logging.info('%s should be formatted as %s', address, final_address)
            formatted_address = formatting.format_geocode(gmaps_api.get_geocode(address=address), include_neighborhood=True)
            if formatted_address != final_address:
                logging.error('formatted address for %r is %r, should be %r', address, formatted_address, final_address)
                logging.error('%s', gmaps_stub.fetch_raw(address=address))
                self.assertEqual(final_address, formatted_address)

grouping_lists = [
    (['Miami, FL', 'Soma, SF, CA', 'Williamsburg, Brooklyn'], ['Miami, FL', 'South of Market, San Francisco, CA', 'Brooklyn, New York, NY']),
    (['Brooklyn', 'Williamsburg, Brooklyn'], ['Brooklyn', 'Williamsburg, Brooklyn']),
    (['SOMA, SF, CA', '6 5th Street, SF, CA'], ['South of Market', 'South of Market']),
    (['Bay Area', '6 5th Street, SF, CA'], ['San Francisco Bay Area, CA', 'South of Market, San Francisco, CA']),
    (['Shibuya', 'Ginza'], ['Shibuya, Tokyo', u'Ginza, Chūō, Tokyo']),
    (['Shibuya', 'Ginza', 'Osaka'], ['Shibuya, Tokyo', u'Ginza, Chūō, Tokyo', 'Osaka, Osaka Prefecture']),
    (['Nagoya', 'Sydney'], ['Nagoya, Aichi Prefecture, Japan', 'Sydney, NSW, Australia']),
]

class TestMultiLocationFormatting(GmapsTestCase):
    def runTest(self):
        for addresses, reformatted_addresses in grouping_lists:
            logging.info("Formatting addresses: %s", addresses)
            logging.info("Intended reformatted addresses: %r", reformatted_addresses)
            geocodes = [gmaps_api.get_geocode(address=address) for address in addresses]
            reformatted_parts = formatting.format_geocodes(geocodes, include_neighborhood=True)
            logging.info("Reformatted addresses: %r", reformatted_parts)
            self.assertEqual(reformatted_parts, reformatted_addresses)


if __name__ == '__main__':
    TestLocationFormatting().runTest()
    TestMultiLocationFormatting().runTest()
