from google.appengine.ext import ndb

import fb_api

TOPIC_DANCER = 'TOPIC_DANCER'
TOPIC_DANCE_CREW = 'TOPIC_DANCE_CREW'
TOPIC_EVENT = 'TOPIC_EVENT'
TOPIC_DANCE_STYLE = 'TOPIC_DANCE_STYLE'

ALL_TOPICS = [
    TOPIC_DANCER,
    TOPIC_DANCE_CREW,
    TOPIC_EVENT,
    TOPIC_DANCE_STYLE,
]

class Topic(ndb.Model):
    _use_cache = False
    graph_id = ndb.StringProperty()

    topic_class = ndb.StringProperty(choices=ALL_TOPICS)

    url_path = ndb.StringProperty()
    override_title = ndb.StringProperty()
    override_description = ndb.StringProperty()
    override_image = ndb.StringProperty()

    # These will be OR-ed together
    search_keywords = ndb.StringProperty(repeated=True)

    youtube_channel = ndb.StringProperty()
    youtube_query = ndb.StringProperty()

    creation_time = ndb.DateTimeProperty(indexed=False, auto_now_add=True)


class LookupTopicPage(fb_api.LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('info', cls.url('%s' % object_id)),
            ('picture', cls.url('%s/picture?type=large&redirect=false' % object_id)),
        ]
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (object_id, 'OBJ_TOPIC_PAGE')
