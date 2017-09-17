from dancedeets.event_scraper import thing_scraper
from dancedeets.test_utils import unittest


class TestParseLink(unittest.TestCase):
    def runTest(self):
        link = "https://m.facebook.com/events/?ref=bookmark&__user=1069102331#!/events/129050660619031/guests/maybe?ref=bookmark&notif_t=plan_mall_acting"
        p = thing_scraper.parsed_event_link(link)
        self.assertEqual(p.path, '/events/129050660619031/guests/maybe')
