from event_scraper import potential_events
from event_scraper import thing_db
from test_utils import unittest


class TestDiscoveredEvent(unittest.TestCase):
    def testHashing(self):
        source = thing_db.Source(id="source_id")
        source.put()
        a = potential_events.DiscoveredEvent("event_id", source, thing_db.FIELD_FEED)
        b = potential_events.DiscoveredEvent("event_id", source, thing_db.FIELD_FEED)
        self.assertEqual(a, b)
        c = set()
        c.add(a)
        c.add(b)
        self.assertEqual(list(c), [a])
