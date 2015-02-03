# -*-*- encoding: utf-8 -*-*-

import unittest

import gmaps
import gmaps_local
import location_formatting

def format_address(address):
    gmaps_data = gmaps_local.fetch_raw_cached(address=address)
    geocode = gmaps.parse_geocode(gmaps_data)
    result = location_formatting.format_address(geocode)
    return result

def format_address_parts(address):
    gmaps_data = gmaps_local.fetch_raw_cached(address=address)
    geocode = gmaps.parse_geocode(gmaps_data)
    result = location_formatting.get_formatting_parts(geocode)
    return result

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
}


class TestLocationFormatting(unittest.TestCase):
    def runTest(self):
        for address, final_address in formatting_reg_data.iteritems():
            formatted_address = format_address(address)
            if formatted_address != final_address:
                print 'formatted address for %r is %r, should be %r' % (address, formatted_address, final_address)
                print gmaps.fetch_json(address=address, fetch_raw=gmaps_local.fetch_raw_cached)
                self.assertEqual(final_address, formatted_address)

grouping_lists = [
    (['Miami, FL', 'Soma, SF, CA', 'Williamsburg, Brooklyn'], ['Miami, FL', 'San Francisco, CA', 'New York, NY']),
    (['Brooklyn', 'Williamsburg, Brooklyn'], ['Brooklyn', 'Williamsburg, Brooklyn']),
    (['SOMA, SF, CA', '6 5th Street, SF, CA'], ['South of Market', 'South of Market']),
    (['Bay Area', '6 5th Street, SF, CA'], ['San Francisco Bay Area', 'South of Market, San Francisco']),
    (['Shibuya', 'Ginza'], ['Shibuya', 'Ginza, Chuo']),
    (['Shibuya', 'Ginza', 'Osaka'], ['Shibuya, Tokyo', 'Chuo, Tokyo', 'Osaka, Osaka Prefecture']),
    (['Nagoya', 'Sydney'], ['Nagoya, Aichi Prefecture, Japan', 'Sydney, NSW, Australia']),
]

class TestMultiLocationFormatting(unittest.TestCase):
    def runTest(self):
        for addresses, reformatted_addresses in grouping_lists:
            gmaps_parts = [format_address_parts(address) for address in addresses]
            reformatted_parts = location_formatting.format_addresses(gmaps_parts)
            self.assertEqual(reformatted_parts, reformatted_addresses)


if __name__ == '__main__':
    TestLocationFormatting().runTest()
    TestMultiLocationFormatting().runTest()
