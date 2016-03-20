# -*-*- encoding: utf-8 -*-*-

import datetime
import mock

import fb_api
from events import eventdata
from events import event_updates
from pubsub import pubsub
from test_utils import unittest

FB_EVENT = {
    'info': {
        'name': 'Some really long name here that just keeps on going and may or may not ever get truncated, but we will just have to wait and see',
    }
}


class TestPublishEvent(unittest.TestCase):
    @mock.patch('keys.get')
    @mock.patch('oauth2.Client.request')
    @mock.patch('twitter.Twitter')
    def runTest(self, Twitter, Client_request, keys_get):
        keys_get.return_value = 'dummy_key'

        twitter_instance = Twitter.return_value
        twitter_instance.help.configuration.return_value = {
            'short_url_length': 22,
            'characters_reserved_per_media': 24,
        }

        # No-op works with with no tokens
        pubsub.pull_and_publish_event()

        # No-op works with a freshly created token
        Client_request.return_value = {'status': '200'}, 'oauth_token=token&oauth_token_secret=secret'
        pubsub.twitter_oauth1('user_id', 'token_nickname', None)
        pubsub.twitter_oauth2('token', 'verifier')
        pubsub.pull_and_publish_event()

        # Now when we add a token to the pull queue, it will get run
        event_id = '383948038362054'
        fbl = fb_api.FBLookup(None, None)
        fb_event = fbl.get(fb_api.LookupEvent, event_id)

        db_event = eventdata.DBEvent.get_or_insert(event_id)
        event_updates.update_and_save_events([(db_event, fb_event)])
        db_event.put()
        pubsub.eventually_publish_event(event_id)

        pubsub.pull_and_publish_event()
        # Check that Twitter().statuses.update(...) was called
        self.assertTrue(Twitter.return_value.statuses.update.called)


class TestImports(unittest.TestCase):
    def runTest(self):
        config = {
            'short_url_length': 22,
            'characters_reserved_per_media': 24,
        }

        class DBEvent(eventdata.DBEvent):
            fb_event_id = '555'
            start_time = datetime.datetime(2010, 1, 1, 12)
            actual_city_name = 'Sacramento, CA, United States'
            fb_event = FB_EVENT
        url = 'http://www.dancedeets.com/events/555/?utm_campaign=autopost&utm_medium=share&utm_source=twitter_feed'
        self.assertEqual(
            pubsub.format_twitter_post(config, DBEvent(), media=False, handles=[]),
            u'2010/01/01: Sacramento, CA, United States: Some really long name here that just keeps on going and may or may not ev… %s' % url)
        self.assertEqual(
            pubsub.format_twitter_post(config, DBEvent(), media=False, handles=['@name']),
            u'2010/01/01: Sacramento, CA, United States: Some really long name here that just keeps on going and may or may … %s @name' % url)
        self.assertEqual(
            pubsub.format_twitter_post(config, DBEvent(), media=False, handles=['@name1', '@name2', '@name3', '@name4', '@name5', '@name6', '@name7']),
            u'2010/01/01: Sacramento, CA, United States: Some really long name here that just k… %s @name1 @name2 @name3 @name4 @name5' % url)
        self.assertEqual(
            pubsub.format_twitter_post(config, DBEvent(), media=False, handles=['@mspersia', '@grooveologydc', '@groovealils', '@dam_sf', '@mishmashboutique']),
            u'2010/01/01: Sacramento, CA, United States: Some really long name here that jus… %s @mspersia @grooveologydc @groovealils' % url)
        self.assertEqual(
            pubsub.format_twitter_post(config, DBEvent(), media=False, handles=['@jodywisternoff', '@jodywisternoff', '@Lane8music']),
            u'2010/01/01: Sacramento, CA, United States: Some really long name here that just keep… %s @jodywisternoff @jodywisternoff' % url)
