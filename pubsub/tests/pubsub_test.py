# -*-*- encoding: utf-8 -*-*-

import unittest
from pubsub import pubsub

FB_EVENT = {
    'info': {
        'id': '555',
        'name': 'Some really long name here that just keeps on going and may or may not ever get truncated, but we will just have to wait and see',
        'start_time': '2010-01-01T12:00:00',
    }
}
class TestImports(unittest.TestCase):
    def runTest(self):
        class DBEvent:
            actual_city_name = 'Sacramento, CA, United States'
        self.assertEqual(pubsub.format_twitter_post(DBEvent(), FB_EVENT, media=False, handles=[]),
            u'2010/01/01: Sacramento, CA, United States: Some really long name here that just keeps on going and may or may not ev… http://www.dancedeets.com/events/555/')
        self.assertEqual(pubsub.format_twitter_post(DBEvent(), FB_EVENT, media=False, handles=['@name']),
            u'2010/01/01: Sacramento, CA, United States: Some really long name here that just keeps on going and may or may … http://www.dancedeets.com/events/555/ @name')
        self.assertEqual(pubsub.format_twitter_post(DBEvent(), FB_EVENT, media=False, handles=['@name1', '@name2', '@name3', '@name4', '@name5', '@name6', '@name7']),
            u'2010/01/01: Sacramento, CA, United States: Some really long name here that just k… http://www.dancedeets.com/events/555/ @name1 @name2 @name3 @name4 @name5')
        self.assertEqual(pubsub.format_twitter_post(DBEvent(), FB_EVENT, media=False, handles=['@mspersia', '@grooveologydc', '@groovealils', '@dam_sf', '@mishmashboutique']),
            u'2010/01/01: Sacramento, CA, United States: Some really long name here that jus… http://www.dancedeets.com/events/555/ @mspersia @grooveologydc @groovealils')
        self.assertEqual(pubsub.format_twitter_post(DBEvent(), FB_EVENT, media=False, handles=['@jodywisternoff', '@jodywisternoff', '@Lane8music']),
            u'2010/01/01: Sacramento, CA, United States: Some really long name here that just keep… http://www.dancedeets.com/events/555/ @jodywisternoff @jodywisternoff')

