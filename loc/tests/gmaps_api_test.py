# -*-*- encoding: utf-8 -*-*-

import unittest

from loc import gmaps_api
from loc import gmaps_stub

class TestGetCountry(unittest.TestCase):
    def setUp(self):
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.gmaps_stub = gmaps_stub.Stub()
        self.gmaps_stub.activate()

    def tearDown(self):
        self.gmaps_stub.deactivate()


    def runTest(self):
        self.assertEqual('US', gmaps_api.get_geocode(address='San Francisco').country())
        self.assertEqual('JP', gmaps_api.get_geocode(address='Tokyo').country())
        # Really long byte-string
        self.assertEqual('RU', gmaps_api.get_geocode(address=u"г.Сочи , ул.Навагинская 9 / 3 этаж...Молодёжный Творческий Центр им.Артура Тумасяна, Творческий Клуб \" Чип Бар \"").country())
