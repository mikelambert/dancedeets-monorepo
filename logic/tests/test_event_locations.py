#!/usr/bin/python

import math
import unittest

from google.appengine.ext import testbed

from events import eventdata
import fb_api
import fb_api_stub
from logic import event_locations

MIKE_ID = '701004'
USER_ID = '1000'
EVENT_ID = '299993043349170'

class TestEventLocations(unittest.TestCase):
    def setUp(self):
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate()
        self.batch_lookup = fb_api.CommonBatchLookup(None, None)

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()
        self.fb_api.deactivate()

    def get_event(self, event_id):
        self.batch_lookup.lookup_event(event_id)
        self.batch_lookup.finish_loading()
        fb_event = self.batch_lookup.data_for_event(event_id)
        return fb_event

    def test_get_address_for_fb_event(self):
        fb_event = self.get_event(EVENT_ID)
        self.assertEqual(event_locations.get_address_for_fb_event(fb_event), "Hype Dance, 67 Earl Street")

class TestLocationInfo(TestEventLocations):
    def setUp(self):
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate()
        self.batch_lookup = fb_api.CommonBatchLookup(None, None)

    def tearDown(self):
        self.fb_api.deactivate()

    def assertNearEqual(self, a, b, delta=0.00001):
        if type(a) == tuple:
            for x, y in zip(a, b):
                self.assertNearEqual(x, y, delta=delta)
        else:
            assert abs(a-b) < delta

    def test_SimpleVenue(self):
        fb_event = self.get_event(EVENT_ID)
        location_info = event_locations.LocationInfo(self.batch_lookup, fb_event, debug=True)
        self.assertEqual(location_info.overridden_address, None)
        self.assertEqual(location_info.remapped_address, None)
        self.assertEqual(location_info.fb_address, 'Hype Dance, 67 Earl Street')
        self.assertEqual(location_info.final_city, 'Sheffield, United Kingdom')
        self.assertNearEqual(location_info.final_latlng, (53.375206800000001, -1.4709795999999999))
        self.assertEqual(location_info.exact_from_event, False)

    def test_NoVenue(self):
        fb_event = self.get_event(100)
        location_info = event_locations.LocationInfo(self.batch_lookup, fb_event, debug=True)
        self.assertEqual(location_info.overridden_address, None)
        self.assertEqual(location_info.remapped_address, None)
        self.assertEqual(location_info.fb_address, 'Somewhere in San Francisco')
        self.assertEqual(location_info.final_city, 'San Francisco, CA, US')
        self.assertNearEqual(location_info.final_latlng, (37.774929499999999, -122.4194155))
        self.assertEqual(location_info.exact_from_event, False)


    def test_NoVenueWithRemap(self):
        fb_event = self.get_event(100)

        try:
            event_locations.update_remapped_address(self.batch_lookup, fb_event, 'Oakland, CA')

            location_info = event_locations.LocationInfo(self.batch_lookup, fb_event, debug=True)
            self.assertEqual(location_info.overridden_address, None)
            self.assertEqual(location_info.remapped_address, 'Oakland, CA')
            self.assertEqual(location_info.fb_address, 'Somewhere in San Francisco')
            self.assertEqual(location_info.final_city, 'Oakland, CA, US')
            self.assertNearEqual(location_info.final_latlng, (37.804363700000003, -122.2711137))
            self.assertEqual(location_info.exact_from_event, False)

            event_locations.update_remapped_address(self.batch_lookup, fb_event, '')
            self.test_NoVenue() # should be the same as before
        finally:
            event_locations.update_remapped_address(self.batch_lookup, fb_event, '')

    def test_Override(self):
        db_event = eventdata.DBEvent(address='San Jose, CA')
        fb_event = self.get_event(100)

        location_info = event_locations.LocationInfo(self.batch_lookup, fb_event, db_event=db_event, debug=True)
        self.assertEqual(location_info.overridden_address, 'San Jose, CA')
        self.assertEqual(location_info.remapped_address, None)
        self.assertEqual(location_info.fb_address, 'Somewhere in San Francisco')
        self.assertEqual(location_info.final_city, 'San Jose, CA, US')
        self.assertNearEqual(location_info.final_latlng, (37.339385700000001, -121.89495549999999))
        self.assertEqual(location_info.exact_from_event, False)

    def test_Online(self):
        db_event = eventdata.DBEvent(address=event_locations.ONLINE_ADDRESS)
        fb_event = self.get_event(100)

        location_info = event_locations.LocationInfo(self.batch_lookup, fb_event, db_event=db_event, debug=True)
        self.assertEqual(location_info.overridden_address, event_locations.ONLINE_ADDRESS)
        self.assertEqual(location_info.remapped_address, None)
        self.assertEqual(location_info.fb_address, 'Somewhere in San Francisco')
        self.assertEqual(location_info.final_city, event_locations.ONLINE_ADDRESS)
        self.assertEqual(location_info.final_latlng, None)
        self.assertEqual(location_info.is_online_event(), True)
        self.assertEqual(location_info.actual_city(), None)
        self.assertEqual(location_info.latlong(), (None, None))
        self.assertEqual(location_info.exact_from_event, False)

    def test_None(self):
        db_event = eventdata.DBEvent(address='ungeocodeable mess of crap')
        fb_event = self.get_event(100)

        location_info = event_locations.LocationInfo(self.batch_lookup, fb_event, db_event=db_event, debug=True)
        self.assertEqual(location_info.final_city, None)
        self.assertEqual(location_info.final_latlng, None)
        self.assertEqual(location_info.exact_from_event, False)

    def test_TBD(self):
        db_event = eventdata.DBEvent(address='San Francisco, CA')
        fb_event = self.get_event(100)

        try:
            event_locations.update_remapped_address(self.batch_lookup, fb_event, 'TBD')

            location_info = event_locations.LocationInfo(self.batch_lookup, fb_event, db_event=db_event, debug=True)
            self.assertEqual(location_info.overridden_address, 'San Francisco, CA')
            self.assertEqual(location_info.remapped_address, 'TBD')
            self.assertEqual(location_info.needs_override_address(), True)

            location_info = event_locations.LocationInfo(self.batch_lookup, fb_event, debug=True)
            self.assertEqual(location_info.overridden_address, None)
            self.assertEqual(location_info.remapped_address, 'TBD')
            self.assertEqual(location_info.needs_override_address(), True)
            self.assertEqual(location_info.exact_from_event, False)

        finally:
            event_locations.update_remapped_address(self.batch_lookup, fb_event, '')

    def test_VenueWithLatLong(self):
        fb_event = self.get_event(437418756269948)

        location_info = event_locations.LocationInfo(self.batch_lookup, fb_event, debug=True)
        self.assertEqual(location_info.overridden_address, None)
        self.assertEqual(location_info.remapped_address, None)
        self.assertEqual(location_info.fb_address, 'Mexico City, D.F., Mexico')
        self.assertEqual(location_info.final_city, 'Mexico City, D.F., Mexico')
        self.assertNearEqual(location_info.final_latlng, (19.400437272727, -99.132922272727))
        self.assertEqual(location_info.exact_from_event, True)

    def test_NothingAtAll(self):
        fb_event = self.get_event(101)

        location_info = event_locations.LocationInfo(self.batch_lookup, fb_event, debug=True)
        self.assertEqual(location_info.overridden_address, None)
        self.assertEqual(location_info.remapped_address, None)
        self.assertEqual(location_info.fb_address, '')
        self.assertEqual(location_info.final_city, None)
        self.assertEqual(location_info.final_latlng, None)
        self.assertEqual(location_info.exact_from_event, False)

    def test_EasyLatLong(self):
        fb_event = self.get_event(102)

        location_info = event_locations.LocationInfo(self.batch_lookup, fb_event, debug=True)
        self.assertEqual(location_info.overridden_address, None)
        self.assertEqual(location_info.remapped_address, None)
        self.assertEqual(location_info.fb_address, 'San Francisco, CA, US')
        self.assertEqual(location_info.final_city, 'San Francisco, CA, US')
        self.assertNearEqual(location_info.final_latlng, (37.774929499999999, -122.4194155))
        self.assertEqual(location_info.exact_from_event, True)


