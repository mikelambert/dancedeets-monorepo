
from event_scraper import thing_scraper
from test_utils import fb_api_stub
from test_utils import unittest

class TestSourceCreatingEvent(unittest.TestCase):
    def runTest(self):
        # tests that the event creation status post gets correctly captured
        data = fb_api_stub.get_object('701004.391260537595682.OBJ_THING_FEED')
        discovered_list = thing_scraper.build_discovered_from_feed(None, data['feed']['data'])
        discovered = discovered_list[0]
        self.assertEqual(discovered.event_id, u'459081844137306')
        self.assertEqual(discovered.source, None)
        self.assertEqual(discovered.extra_source_id, u'391260537595682')

class TestParseLink(unittest.TestCase):
    def runTest(self):
        link = "https://m.facebook.com/events/?ref=bookmark&__user=1069102331#!/events/129050660619031/guests/maybe?ref=bookmark&notif_t=plan_mall_acting"
        p = thing_scraper.parsed_event_link(link)
        self.assertEqual(p.path, '/events/129050660619031/guests/maybe')
