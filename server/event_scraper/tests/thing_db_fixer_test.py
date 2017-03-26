import urllib

import fb_api
from event_scraper import potential_events
from event_scraper import thing_db
from test_utils import unittest
from util import deferred

fields_str = '%2C'.join(fb_api.OBJ_SOURCE_FIELDS)
VERSION = fb_api.LookupThingFeed.version
URL_111 = '/%s/111' % VERSION # ?fields=%s' % fields_str
URL_222 = '/%s/222' % VERSION # ?fields=%s' % fields_str
URL_111_FEED = '/%s/111/feed?%s' % (VERSION, urllib.urlencode(dict(fields='created_time,updated_time,from,link,actions,message')))
URL_222_FEED = '/%s/222/feed?%s' % (VERSION, urllib.urlencode(dict(fields='created_time,updated_time,from,link,actions,message')))
URL_111_EVENTS = '/%s/111/events?%s' % (VERSION, urllib.urlencode(dict(fields='id,updated_time')))
URL_222_EVENTS = '/%s/222/events?%s' % (VERSION, urllib.urlencode(dict(fields='id,updated_time')))

class TestThingDBFixer(unittest.TestCase):

    def mark_as_error_and_reload(self, fbl):

        # Now let's "rename" the source to be id 222
        error = (400, {"error": {"message": "Page ID 111 was migrated to page ID 222.  Please update your API calls to the new ID", "code": 21, "type": "OAuthException"}})
        fb_api.FBAPI.results.update({
            URL_111: error,
            URL_111_FEED: error,
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
            URL_111: (200, {'id': '111', 'name': 'page 1', 'likes': 1}),
            URL_111_FEED: (200, {'data': []}),
            URL_111_EVENTS: (200, {'data': []}),
            URL_222: (200, {'id': '222', 'name': 'page 2', 'likes': 1}),
            URL_222_FEED: (200, {'data': []}),
            URL_222_EVENTS: (200, {'data': []}),
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
            URL_111: (200, {'id': '111', 'name': 'page 1', 'likes': 1}),
            URL_111_FEED: (200, {'data': []}),
        })
        source = thing_db.create_source_for_id('111', result)
        source.num_all_events = 5
        source.put()

        pe = potential_events.PotentialEvent(key_name="333")
        pe.set_sources([potential_events.PESource("111", thing_db.FIELD_FEED), potential_events.PESource("222", thing_db.FIELD_FEED)])
        pe.put()

        self.mark_as_error_and_reload(fbl)

        pe = potential_events.PotentialEvent.get_by_key_name("333")
        #STR_ID_MIGRATE
        self.assertEqual(pe.sources(), [potential_events.PESource("222", thing_db.FIELD_FEED)])
