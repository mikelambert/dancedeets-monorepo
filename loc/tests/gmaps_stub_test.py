# -*-*- encoding: utf-8 -*-*-

import logging

from loc import gmaps_stub
from test_utils import unittest

formatting_reg_data = {
    u'address_u__u6e0b_u8c37_': dict(address=u'渋谷'),
    u'address__soma__sf__ca_': dict(address='SOMA, SF, CA'),
    u'latlng__12345_0123456789__12345_01234': dict(latlng=(12345.0123456789, 12345.0123456789)),
}


class TestLocationFormatting(unittest.TestCase):
    def runTest(self):
        for key, params in formatting_reg_data.iteritems():
            logging.info('%r should be formatted as %s', params, key)
            string_key = gmaps_stub._geocode_key(**params)
            self.assertEqual(string_key, key)
