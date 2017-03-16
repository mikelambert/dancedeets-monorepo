#!/usr/bin/python
# -*-*- encoding: utf-8 -*-*-

from events import eventdata
from events import event_locations
import fb_api
from loc import gmaps_stub
from test_utils import fb_api_stub
from test_utils import unittest

MIKE_ID = '701004'
USER_ID = '1000'
EVENT_ID = '299993043349170'

class TestEventLocations(unittest.TestCase):
    def setUp(self):
        super(TestEventLocations, self).setUp()
        self.fbl = fb_api.FBLookup("dummyid", None)

    def get_event(self, event_id):
        return self.fbl.get(fb_api.LookupEvent, event_id)

    def assertNearEqual(self, a, b, delta=0.01):
        if type(a) == tuple:
            for x, y in zip(a, b):
                self.assertNearEqual(x, y, delta=delta)
        else:
            assert abs(a-b) < delta, "a=%s,b=%s, a-b=%s < delta=%s" % (a, b, (a-b), delta)

class TestGetAddressForFbEvent(TestEventLocations):
    def runTest(self):
        fb_event = self.get_event(EVENT_ID)
        self.assertEqual(event_locations.get_address_for_fb_event(fb_event), "Hype Dance, 67 Earl Street, Sheffield")

class TestSimpleVenue(TestEventLocations):
    def runTest(self):
        fb_event = self.get_event(EVENT_ID)
        location_info = event_locations.LocationInfo(fb_event, debug=True)
        self.assertEqual(location_info.overridden_address, None)
        self.assertEqual(location_info.remapped_address, None)
        self.assertEqual(location_info.fb_address, 'Hype Dance, 67 Earl Street, Sheffield')
        self.assertEqual(location_info.final_city, 'Sheffield, United Kingdom')
        self.assertNearEqual(location_info.latlong(), (53.375206800000001, -1.4709795999999999))

class TestNoVenue(TestEventLocations):
    def runTest(self):
        fb_event = self.get_event('100')
        location_info = event_locations.LocationInfo(fb_event, debug=True)
        self.assertEqual(location_info.overridden_address, None)
        self.assertEqual(location_info.remapped_address, None)
        self.assertEqual(location_info.fb_address, 'San Francisco')
        self.assertEqual(location_info.final_city, 'San Francisco, CA, United States')
        self.assertNearEqual(location_info.latlong(), (37.774929499999999, -122.4194155))

class TestNoVenueWithRemap(TestNoVenue):
    def runTest(self):
        fb_event = self.get_event('100')

        try:
            event_locations.update_remapped_address(fb_event, 'Oakland, CA')

            location_info = event_locations.LocationInfo(fb_event, debug=True)
            self.assertEqual(location_info.overridden_address, None)
            self.assertEqual(location_info.remapped_address, 'Oakland, CA')
            self.assertEqual(location_info.fb_address, 'San Francisco')
            self.assertEqual(location_info.final_city, 'Oakland, CA, United States')
            self.assertNearEqual(location_info.latlong(), (37.804363700000003, -122.2711137))

            event_locations.update_remapped_address(fb_event, '')
            super(TestNoVenueWithRemap, self).runTest() # should be the same as before
        finally:
            event_locations.update_remapped_address(fb_event, '')

class TestOverride(TestEventLocations):
    def runTest(self):
        db_event = eventdata.DBEvent(address='San Jose, CA')
        fb_event = self.get_event('100')

        location_info = event_locations.LocationInfo(fb_event, db_event=db_event, debug=True)
        self.assertEqual(location_info.overridden_address, 'San Jose, CA')
        self.assertEqual(location_info.remapped_address, None)
        self.assertEqual(location_info.fb_address, 'San Francisco')
        self.assertEqual(location_info.final_city, 'San Jose, CA, United States')
        self.assertNearEqual(location_info.latlong(), (37.339385700000001, -121.89495549999999))

class TestOnline(TestEventLocations):
    def runTest(self):
        db_event = eventdata.DBEvent(address=event_locations.ONLINE_ADDRESS)
        fb_event = self.get_event('100')

        location_info = event_locations.LocationInfo(fb_event, db_event=db_event, debug=True)
        self.assertEqual(location_info.overridden_address, event_locations.ONLINE_ADDRESS)
        self.assertEqual(location_info.remapped_address, None)
        self.assertEqual(location_info.fb_address, 'San Francisco')
        self.assertEqual(location_info.final_city, event_locations.ONLINE_ADDRESS)
        self.assertEqual(location_info.is_online_event(), True)
        self.assertEqual(location_info.actual_city(), None)
        self.assertEqual(location_info.latlong(), (None, None))

class TestNewEventPlaceAPI(TestEventLocations):
    def runTest(self):
        fb_event = self.get_event('103')

        location_info = event_locations.LocationInfo(fb_event, debug=True)
        self.assertEqual(location_info.overridden_address, None)
        self.assertEqual(location_info.remapped_address, None)
        self.assertEqual(location_info.fb_address, u'Jingsta, \u795e\u5bae\u524d2-18-7\u5916\u82d1\u30d3\u30ebB1, Shibuya-ku, Tokyo, Japan')
        self.assertEqual(location_info.final_city, u'18, Shibuya-ku, T\u014dky\u014d-to, Japan')
        self.assertEqual(location_info.is_online_event(), False)
        self.assertEqual(location_info.actual_city(), u'18, Shibuya-ku, T\u014dky\u014d-to, Japan')
        self.assertEqual(location_info.latlong(), (35.6724529, 139.7098159))

class TestNone(TestEventLocations):
    def runTest(self):
        db_event = eventdata.DBEvent(address='ungeocodeable mess of crap')
        fb_event = self.get_event('100')

        location_info = event_locations.LocationInfo(fb_event, db_event=db_event, debug=True)
        self.assertEqual(location_info.final_city, None)
        self.assertEqual(location_info.latlong(), (None, None))

class TestTBD(TestEventLocations):
    def runTest(self):
        db_event = eventdata.DBEvent(address='San Francisco, CA')
        fb_event = self.get_event('100')

        try:
            event_locations.update_remapped_address(fb_event, 'TBD')

            location_info = event_locations.LocationInfo(fb_event, db_event=db_event, debug=True)
            self.assertEqual(location_info.overridden_address, 'San Francisco, CA')
            self.assertEqual(location_info.remapped_address, 'TBD')
            self.assertEqual(location_info.needs_override_address(), True)

            location_info = event_locations.LocationInfo(fb_event, debug=True)
            self.assertEqual(location_info.overridden_address, None)
            self.assertEqual(location_info.remapped_address, 'TBD')
            self.assertEqual(location_info.needs_override_address(), True)

        finally:
            event_locations.update_remapped_address(fb_event, '')

class TestNothingAtAll(TestEventLocations):
    def runTest(self):
        fb_event = self.get_event('101')

        location_info = event_locations.LocationInfo(fb_event, debug=True)
        self.assertEqual(location_info.overridden_address, None)
        self.assertEqual(location_info.remapped_address, None)
        self.assertEqual(location_info.fb_address, None)
        self.assertEqual(location_info.final_city, None)
        self.assertEqual(location_info.latlong(), (None, None))

class TestEasyLatLong(TestEventLocations):
    def runTest(self):
        fb_event = self.get_event('102')

        location_info = event_locations.LocationInfo(fb_event, debug=True)
        self.assertEqual(location_info.overridden_address, None)
        self.assertEqual(location_info.remapped_address, None)
        self.assertEqual(location_info.fb_address, 'San Francisco, CA, United States')
        self.assertEqual(location_info.final_city, 'San Francisco, CA, United States')
        self.assertNearEqual(location_info.latlong(), (37.774929499999999, -122.4194155))

def gen_event_with_location(loc):
    return {
        "empty": False,
        "info": {
            "name": "event with configured place name",
            "place": {
                "name": loc,
            }
        }
    }

class TestGetString(unittest.TestCase):
    def runTest(self):

        self.assertEqual('New Taipei City, Taiwan', event_locations.LocationInfo(gen_event_with_location(u'捷運板橋站練舞')).final_city)
        self.assertEqual((37.8693878, -122.2623099), event_locations.LocationInfo(gen_event_with_location(u'   Haas Pavilion, Berkeley, CA 94720, United States')).geocode.latlng())
