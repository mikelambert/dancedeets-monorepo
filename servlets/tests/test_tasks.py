import unittest
from webtest import TestApp

from google.appengine.ext import testbed

from events import eventdata
from events import users
import main
import fb_api_stub

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
        #TODO(lambert): To enable this, we need to figure out how to make slow-queue exist
        #self.testbed.init_taskqueue_stub()
        
        e = eventdata.DBEvent(key_name=EVENT_ID)
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

    def testLoadEvents(self):
        app.get('/tasks/load_events?user_id=%s&event_ids=%s' % (MIKE_ID, EVENT_ID))
    def testLoadEventAttending(self):
        app.get('/tasks/load_event_attending?user_id=%s&event_ids=%s' % (MIKE_ID, EVENT_ID))

    def testReloadFutureEvents(self):
        app.get('/tasks/reload_future_events?user_id=%s&event_ids=%s' % (MIKE_ID, EVENT_ID))

    def testReloadPastEvents(self):
        app.get('/tasks/reload_future_events?user_id=%s&event_ids=%s' % (MIKE_ID, EVENT_ID))

"""
def test_2():
    print app.get('/tasks/load_users?user_id=701004&user_ids=701004')
def test_4():
    print app.get('/tasks/track_newuser_friends?user_id=701004')
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
