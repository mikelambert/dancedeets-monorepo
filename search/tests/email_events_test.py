import fb_api
from search import email_events
from test_utils import fixtures
from test_utils import unittest

class TestSearch(unittest.TestCase):
    def runTest(self):
        user = fixtures.create_user()
        event = fixtures.create_event()
        fixtures.index_events(self.testbed)

        fbl = user.get_fblookup()
        # Fetch it now so it's cached before email_for_user accesses it
        fbl.get(fb_api.LookupUser, user.fb_uid)

        message = email_events.email_for_user(user, fbl, should_send=False)
        self.assertIn('http://www.dancedeets.com/events/%s/' % event.fb_event_id, message.html)
        self.assertTrue(message, "Emailer did not email the user")

