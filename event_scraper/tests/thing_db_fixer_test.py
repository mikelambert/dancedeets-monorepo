import unittest

from google.appengine.ext import deferred
from google.appengine.ext import testbed

import fb_api
from test_utils import fb_api_stub
from event_scraper import potential_events
from event_scraper import thing_db

class TestThingDBFixer(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.taskqueue_stub = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        self.fb_api = fb_api_stub.Stub()
        self.fb_api.activate()

    def tearDown(self):
        self.fb_api.deactivate()
        self.testbed.deactivate()

    def mark_as_error_and_reload(self, fbl):
        # Now let's "rename" the source to be id 222
        error = (400, {"error": {"message": "Page ID 111 was migrated to page ID 222.  Please update your API calls to the new ID", "code": 21, "type": "OAuthException"}})
        fb_api.FBAPI.results.update({
            '/v2.2/111': error,
            '/v2.2/111/feed': error,
        })
        fbl.clear_local_cache()

        # Loading it again should trigger a deferred task to rename to 222
        try:
            fbl.get(fb_api.LookupThingFeed, '111')
            self.fail("Fetching renamed ID unexpectedly worked")
        except fb_api.NoFetchedDataException:
            pass

        # Let's verify a task got created, and run it now
        tasks = self.taskqueue_stub.get_filtered_tasks()
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        deferred.run(task.payload)

        # We have to handle "in case of queue_name, set the default manually" scenario ourselves
        self.taskqueue_stub.DeleteTask(task.queue_name or 'default', task.name)

    def runTest(self):
        fbl = fb_api.FBLookup('uid', 'access_token')
        fbl.allow_cache = False

        # Set up our facebook backend
        fb_api.FBAPI.results = {
            '/v2.2/111': (200, {'id': '111', 'name': 'page 1', 'likes': 1}),
            '/v2.2/111/feed': (200, {'data': []}),
            '/v2.2/111/events': (200, {'data': []}),
            '/v2.2/222': (200, {'id': '222', 'name': 'page 2', 'likes': 1}),
            '/v2.2/222/feed': (200, {'data': []}),
            '/v2.2/222/events': (200, {'data': []}),
        }

        # Fetch it and construct a source
        result = fbl.get(fb_api.LookupThingFeed, '111')
        source = thing_db.create_source_for_id('111', result)
        source.num_all_events = 5
        source.put()

        source = thing_db.Source.get_by_key_name('111')
        self.assertEquals(source.name, 'page 1')
        
        self.mark_as_error_and_reload(fbl)

        # Let's verify id 111 no longer exists
        source = thing_db.Source.get_by_key_name('111')

        # Now let's load id 222 and verify it exists
        source = thing_db.Source.get_by_key_name('222')
        # And verify that our data from the first one got carried over
        self.assertEquals(source.num_all_events, 5)
        # But the the remaining data comes from the latest FB values for this page id
        self.assertEquals(source.name, 'page 2')

        # Now let's create 111 again, to verify merge works
        fb_api.FBAPI.results.update({
            '/v2.2/111': (200, {'id': '111', 'name': 'page 1', 'likes': 1}),
            '/v2.2/111/feed': (200, {'data': []}),
        })
        source = thing_db.create_source_for_id('111', result)
        source.num_all_events = 5
        source.put()

        pe = potential_events.PotentialEvent(key_name="333")
        #STR_ID_MIGRATE
        pe.source_ids = [111, 222]
        pe.source_fields = [thing_db.GRAPH_TYPE_PROFILE, thing_db.GRAPH_TYPE_PROFILE]
        pe.put()

        self.mark_as_error_and_reload(fbl)

        pe = potential_events.PotentialEvent.get_by_key_name("333")
        #STR_ID_MIGRATE
        self.assertEqual(pe.source_ids, [222])
        self.assertEqual(pe.source_fields, [thing_db.GRAPH_TYPE_PROFILE])
