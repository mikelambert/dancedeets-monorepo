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
            actual_city_name = 'City, State, Country'
        self.assertEqual(pubsub.format_twitter_post(DBEvent(), FB_EVENT, media=False, handles=[]),
            u'2010/01/01: City, State, Country: Some really long name here that just keeps on going and may or may not ever get tr… http://www.dancedeets.com/events/555/')
        self.assertEqual(pubsub.format_twitter_post(DBEvent(), FB_EVENT, media=False, handles=['@name']),
            u'2010/01/01: City, State, Country: Some really long name here that just keeps on going and may or may not ever … http://www.dancedeets.com/events/555/ @name')
        self.assertEqual(pubsub.format_twitter_post(DBEvent(), FB_EVENT, media=False, handles=['@name1', '@name2', '@name3', '@name4', '@name5', '@name6', '@name7']),
            u'2010/01/01: City, State, Country: Some really long name here that just kee… http://www.dancedeets.com/events/555/ @name1 @name2 @name3 @name4 @name5 @name6')
        self.assertEqual(pubsub.format_twitter_post(DBEvent(), FB_EVENT, media=False, handles=['@mspersia', '@grooveologydc', '@groovealils', '@dam_sf', '@mishmashboutique']),
            u'2010/01/01: City, State, Country: Some really long name here that just… http://www.dancedeets.com/events/555/ @mspersia @grooveologydc @groovealils @dam_sf')
