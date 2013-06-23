
import unittest
import fb_api_stub

from logic import thing_scraper

class TestScraper(unittest.TestCase):
    def test_source_creating_event(self):
        # tests that the event creation status post gets correctly captured
        data = fb_api_stub.get_object('701004.391260537595682.OBJ_THING_FEED')
        event_source_combos = thing_scraper.parse_event_source_combos_from_feed(None, data['feed']['data'])
        self.assertEqual(event_source_combos, [(u'459081844137306', None, u'391260537595682')])

    def test_parse_link(self):
        link = "https://m.facebook.com/events/?ref=bookmark&__user=1069102331#!/events/129050660619031/guests/maybe?ref=bookmark&notif_t=plan_mall_acting"
        p = thing_scraper.parsed_event_link(link)
        self.assertEqual(p.path, '/events/129050660619031/guests/maybe')
