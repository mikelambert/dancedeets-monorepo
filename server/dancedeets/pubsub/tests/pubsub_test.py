# -*-*- encoding: utf-8 -*-*-

import datetime
import mock

from dancedeets import fb_api
from dancedeets.events import eventdata
from dancedeets.events import event_updates
from dancedeets.pubsub import pubsub
from dancedeets.pubsub import weekly
from dancedeets.pubsub.twitter import auth_setup
from dancedeets.pubsub.twitter import event
from dancedeets.rankings import cities_db
from dancedeets.search import search_base
from dancedeets.test_utils import unittest

FB_EVENT = {
    'info': {
        'name': 'Some really long name here that just keeps on going and may or may not ever get truncated, but we will just have to wait and see',
    },
    'empty': None,
}


class TestPublishEvent(unittest.TestCase):
    @mock.patch('dancedeets.keys.get')
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
        auth_setup.twitter_oauth1('user_id', 'token_nickname', None)
        auth_setup.twitter_oauth2('token', 'verifier')
        pubsub.pull_and_publish_event()

        # Now when we add a token to the pull queue, it will get run
        event_id = '383948038362054'
        fbl = fb_api.FBLookup(None, None)
        fb_event = fbl.get(fb_api.LookupEvent, event_id)

        db_event = eventdata.DBEvent.get_or_insert(event_id)
        event_updates.update_and_save_fb_events([(db_event, fb_event)], disable_updates=['photo'])
        db_event.put()
        pubsub.eventually_publish_event(event_id)

        pubsub.pull_and_publish_event()
        # Check that Twitter().statuses.update(...) was called
        self.assertTrue(Twitter.return_value.statuses.update.called)


class TestWeeklyPost(unittest.TestCase):
    def runTest(self):
        city = cities_db.City(dict(city_name='Gotham'))
        d = datetime.date(2020, 1, 1)
        week_start = d - datetime.timedelta(days=d.weekday())  # round down to last monday
        search_results = [
            search_base.SearchResult(
                '1', {
                    'name': 'Event 1',
                    'start_time': '2020-01-01T09:00:00',
                }, eventdata.DBEvent(fb_event={
                    'info': {},
                })
            ),
            search_base.SearchResult(
                '2', {
                    'name': 'Event 2',
                    'start_time': '2020-01-01T10:00:00',
                }, eventdata.DBEvent(fb_event={
                    'info': {},
                })
            ),
            search_base.SearchResult(
                '3', {
                    'name': 'Event 3',
                    'start_time': '2020-01-03T09:00:00',
                }, eventdata.DBEvent(fb_event={
                    'info': {},
                })
            ),
        ]
        message = weekly._generate_post_for(city, week_start, search_results)
        contents = message.split('\n\n', 1)[1].rsplit('\n\n', 1)[0]
        self.assertEqual(
            contents, '''\
Wednesday January 1:
- 9:00: Event 1:
  http://dd.events/e-1

- 10:00: Event 2:
  http://dd.events/e-2


Friday January 3:
- 9:00: Event 3:
  http://dd.events/e-3'''
        )


class TestImports(unittest.TestCase):
    def runTest(self):
        config = {
            'short_url_length': 22,
            'characters_reserved_per_media': 24,
        }

        db_event = eventdata.DBEvent(id='555')
        db_event.start_time = datetime.datetime(2010, 1, 1, 12)
        db_event.actual_city_name = 'Sacramento, CA, United States'
        db_event.fb_event = FB_EVENT

        url = 'https://www.dancedeets.com/events/555/some-really-long-name-here-that-just-keeps-on-going-and-may-or-may-not-ever-get-truncated-but-we-will-just-have-to-wait-and-see?utm_campaign=autopost&utm_medium=share&utm_source=twitter_feed'
        self.maxDiff = 1000
        self.assertEqual(
            event.format_twitter_post(config, db_event, media=False, handles=[]),
            u'2010/01/01: Sacramento, CA, United States: Some really long name here that just keeps on going and may or may not ev… %s' %
            url
        )
        self.assertEqual(
            event.format_twitter_post(config, db_event, media=False, handles=['@name']),
            u'2010/01/01: Sacramento, CA, United States: Some really long name here that just keeps on going and may or may … %s @name' %
            url
        )
        self.assertEqual(
            event.format_twitter_post(
                config, db_event, media=False, handles=['@name1', '@name2', '@name3', '@name4', '@name5', '@name6', '@name7']
            ), u'2010/01/01: Sacramento, CA, United States: Some really long name here that just k… %s @name1 @name2 @name3 @name4 @name5' %
            url
        )
        self.assertEqual(
            event.format_twitter_post(
                config, db_event, media=False, handles=['@mspersia', '@grooveologydc', '@groovealils', '@dam_sf', '@mishmashboutique']
            ), u'2010/01/01: Sacramento, CA, United States: Some really long name here that jus… %s @mspersia @grooveologydc @groovealils' %
            url
        )
        self.assertEqual(
            event.format_twitter_post(config, db_event, media=False, handles=['@jodywisternoff', '@jodywisternoff', '@Lane8music']),
            u'2010/01/01: Sacramento, CA, United States: Some really long name here that just keep… %s @jodywisternoff @jodywisternoff' %
            url
        )
