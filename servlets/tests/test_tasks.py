import unittest
from webtest import TestApp

from google.appengine.ext import testbed

from events import eventdata
import fb_api
import main
from test_utils import fb_api_stub
from users import users

app = TestApp(main.application)

MIKE_ID = '701004'
USER_ID = '1000'
EVENT_ID = '299993043349170'

class TestTasks(unittest.TestCase):
    def setUp(self):
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate()
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        #TODO(lambert): move this into some testbed wrapper code, or port upstream
        # This is a bug in the code versions between appengine and its libraries:
        # mapreduce requires a DEFAULT_VERSION_HOSTNAME
        self.testbed.setup_env(overwrite=True,
            DEFAULT_VERSION_HOSTNAME='localhost',
        )
        #TODO(lambert): To enable this, we need to figure out how to make slow-queue exist
        #self.testbed.init_taskqueue_stub()
        
        e = eventdata.DBEvent(id=EVENT_ID)
        e.time_period = eventdata.TIME_FUTURE
        e.put()
        m = users.User(key_name=MIKE_ID)
        m.fb_access_token = "DUMMY"
        m.put()
        u = users.User(key_name=USER_ID)
        u.fb_access_token = "DUMMY"
        u.put()

    def tearDown(self):
        self.testbed.deactivate()
        self.fb_api.deactivate()

class TestLoadEvents(TestTasks):
    def runTest(self):
        app.get('/tasks/load_events?user_id=%s&event_ids=%s' % (MIKE_ID, EVENT_ID))

class TestLoadEventAttending(TestTasks):
    def runTest(self):
        fb_api.FBAPI.results = {
            '/299993043349170/attending': (200, {
                "data": [
                    {"uid": 703278},
                    {"uid": 823422},
            ]})
        }
        app.get('/tasks/load_event_attending?user_id=%s&event_ids=%s' % (MIKE_ID, EVENT_ID))

class TestReloadFutureEvents(TestTasks):
    def runTest(self):
        app.get('/tasks/reload_future_events?user_id=%s&event_ids=%s' % (MIKE_ID, EVENT_ID))

class TestReloadPastEvents(TestTasks):
    def runTest(self):
        app.get('/tasks/reload_future_events?user_id=%s&event_ids=%s' % (MIKE_ID, EVENT_ID))

class TestTrackNewUserFriends(TestTasks):
    def runTest(self):
        fb_api.FBAPI.results = {
            '/v1.0/fql?q=%0ASELECT+uid+FROM+user%0AWHERE+uid+IN+%28SELECT+uid2+FROM+friend+WHERE+uid1+%3D+701004%29%0AAND+is_app_user+%3D+1%0A':
            (200, {
                "data": [
                    # Yes, we sometimes have both strings and integers being returned
                    {"uid": 703278},
                    {"uid": '823422'},
            ]}),
        }
        app.get('/tasks/track_newuser_friends?user_id=%s' % MIKE_ID)

"""
def test_2():
    print app.get('/tasks/load_users?user_id=701004&user_ids=701004')
def test_5():
    print app.get('/tasks/reload_all_users?user_id=701004')
def test_8():
    print app.get('/tasks/email_all_users?user_id=701004')
def test_9():
    print app.get('/tasks/email_user?user_id=701004')

def test_10():
    print app.get('/tasks/load_all_potential_events?user_id=701004')
def test_11():
    print app.get('/tasks/load_potential_events_for_friends?user_id=701004')
def test_12():
    print app.get('/tasks/load_potential_events_for_user?user_id=701004')
def test_13():
    print app.get('/tasks/load_potential_events_from_wall_posts?user_id=701004')
"""

# update cron? this does not work
# tasks/reload_all_users?allow_cache=0
