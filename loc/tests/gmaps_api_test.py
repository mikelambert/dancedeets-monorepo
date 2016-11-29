# -*-*- encoding: utf-8 -*-*-

from loc import gmaps_api
from test_utils import unittest

class TestGetCountry(unittest.TestCase):
    def runTest(self):
        self.assertEqual('US', gmaps_api.lookup_address('San Francisco').country())
        self.assertEqual('JP', gmaps_api.lookup_address('Tokyo').country())
        # Really long byte-string
        self.assertEqual('RU', gmaps_api.lookup_address(u"г.Сочи , ул.Навагинская 9 / 3 этаж...Молодёжный Творческий Центр им.Артура Тумасяна, Творческий Клуб \" Чип Бар \"").country())
