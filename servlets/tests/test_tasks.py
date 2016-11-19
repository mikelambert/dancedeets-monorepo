from webtest import TestApp

from events import eventdata
import fb_api
from loc import gmaps_stub
import main
from test_utils import fb_api_stub
from test_utils import unittest
from users import users
from util import dates

app = TestApp(main.application)

MIKE_ID = '701004'
USER_ID = '1000'
EVENT_ID = '299993043349170'

class TestTasks(unittest.TestCase):
    def setUp(self):
        super(TestTasks, self).setUp()
        e = eventdata.DBEvent(id=EVENT_ID)
        e.search_time_period = dates.TIME_FUTURE
        e.put()
        m = users.User(id=MIKE_ID)
        m.fb_access_token = "DUMMY"
        m.expired_oauth_token = False
        m.put()
        u = users.User(id=USER_ID)
        u.fb_access_token = "DUMMY"
        u.expired_oauth_token = False
        u.put()

class TestLoadEvents(TestTasks):
    def runTest(self):
        app.get('/tasks/load_events?user_id=%s&event_ids=%s' % (MIKE_ID, EVENT_ID))

class TestLoadEventAttending(TestTasks):
    def runTest(self):
        fb_api.FBAPI.results = {
            '/299993043349170/attending': (200, {
                "data": [
                    {"id": "703278"},
                    {"id": "823422"},
            ]})
        }
        app.get('/tasks/load_event_attending?user_id=%s&event_ids=%s' % (MIKE_ID, EVENT_ID))

class TestReloadFutureEvents(TestTasks):
    def runTest(self):
        app.get('/tasks/reload_events?user_id=%s&event_ids=%s&time_period=%s' % (MIKE_ID, EVENT_ID, dates.TIME_FUTURE))

class TestReloadPastEvents(TestTasks):
    def runTest(self):
        app.get('/tasks/reload_events?user_id=%s&event_ids=%s&time_period=%s' % (MIKE_ID, EVENT_ID, dates.TIME_PAST))

class TestTrackNewUserFriends(TestTasks):
    def runTest(self):
        fb_api.FBAPI.results = {
            '/v2.2/701004/friends':
            (200, {
                "data": [
                    {"id": "703278"},
                    {"id": '823422'},
            ]}),
        }
        app.get('/tasks/track_newuser_friends?user_id=%s' % MIKE_ID)

"""
def test_2():
    print app.get('/tasks/load_users?user_id=701004&user_ids=701004')
def test_5():
    print app.get('/tasks/reload_all_users')
def test_8():
    print app.get('/tasks/email_all_users?user_id=701004')
def test_9():
    print app.get('/tasks/email_user?user_id=701004')

def test_10():
    print app.get('/tasks/load_all_potential_events?user_id=dummy')
def test_12():
    print app.get('/tasks/load_potential_events_for_user?user_id=701004')
def test_13():
    print app.get('/tasks/load_potential_events_from_wall_posts?user_id=701004')
"""

# update cron? this does not work
# tasks/reload_all_users?allow_cache=0
