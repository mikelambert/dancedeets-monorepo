
from google.appengine.ext import ndb

from google.appengine.api.search import search

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

class StudioClass(ndb.Model):
    # The dev_appserver's query() sometimes returns stale data
    # for objects that were recently set. I'm not entirely sure of the cause,
    # but this ensures that any re-fetches trigger re-loads from
    # the backend systems, so we can check the latest data ourselves.
    _use_cache = False

    def __init__(self, **kwargs):
        if kwargs and 'id' not in kwargs:
            # We need to construct/use a consistent id that stays the same
            # Both to make it easier to update fields, without turning through objects
            # But also to ensure our search index doesn't need to de-index/re-index
            studio_name = kwargs['studio_name']
            start_time = kwargs['start_time']
            teacher = kwargs['teacher']
            computed_id = self.compute_id(studio_name, start_time, teacher)
            kwargs['id'] = computed_id
            search._CheckDocumentId(kwargs['id'])
        super(StudioClass, self).__init__(**kwargs)

    @classmethod
    def compute_id(cls, studio_name, start_time, teacher):
        combined_key = '%s:%s:%s' % (studio_name, start_time.strftime(DATETIME_FORMAT), teacher)
        combined_key = combined_key.replace(' ', '').encode('ascii', 'replace')
        return combined_key[:500]

    recurrence_id = ndb.StringProperty()

    studio_name = ndb.StringProperty()
    source_page = ndb.StringProperty(indexed=False)
    style = ndb.StringProperty(indexed=False)
    teacher = ndb.StringProperty(indexed=False)
    teacher_link = ndb.StringProperty(indexed=False)
    start_time = ndb.DateTimeProperty()
    end_time = ndb.DateTimeProperty(indexed=False)

    auto_categories = ndb.StringProperty(repeated=True)

    latitude = ndb.FloatProperty()
    longitude = ndb.FloatProperty(indexed=False)
    address = ndb.StringProperty(indexed=False)

    scrape_time = ndb.DateTimeProperty(indexed=False)

    @classmethod
    def get_by_ids(cls, id_list, keys_only=False):
        if not id_list:
            return []
        keys = [ndb.Key(cls, x) for x in id_list]
        if keys_only:
            return cls.query(cls.key.IN(keys)).fetch(len(keys), keys_only=True)
        else:
            return ndb.get_multi(keys)
