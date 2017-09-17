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
    graph_id = ndb.StringProperty()

    creation_time = ndb.DateTimeProperty(indexed=False, auto_now_add=True)

    topic_class = ndb.StringProperty(choices=ALL_TOPICS)

    json_data = ndb.JsonProperty()
    fb_data = ndb.JsonProperty()

    def overrides(self):
        try:
            return self.json_data.get('overrides', {})
        except AttributeError:
            return {}

    def init(self):
        try:
            self.json_data
        except AttributeError:
            self.json_data = {}

        # We shouldn't need any tokens to access pages
        if self.graph_id:
            fbl = fb_api.FBLookup(None, None)
            fb_source = fbl.get(LookupTopicPage, self.graph_id)
            self.fb_data = None if fb_source['empty'] else fb_source
        else:
            self.fb_data = None

    def title(self):
        return self.overrides().get('title') or (self.fb_data and self.fb_data['info']['name'])

    def description(self):
        return self.overrides().get('description') or (self.fb_data and self.fb_data['info'].get('about', '')) or ''

    def image_url(self):
        return self.overrides().get('image_url') or (self.fb_data and self.fb_data['info']['cover']['source'])

    url_path = ndb.StringProperty()

    # These will be OR-ed together
    search_keywords = ndb.StringProperty(repeated=True)

    def social(self):
        try:
            return self.json_data.get('social', {})
        except AttributeError:
            return {}

    youtube_channel = ndb.StringProperty()
    youtube_query = ndb.StringProperty()


class LookupTopicPage(fb_api.LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('info', cls.url('%s' % object_id, fields=['id', 'name', 'about', 'cover'])),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (object_id or 'None', 'OBJ_TOPIC_PAGE')
