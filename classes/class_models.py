
from google.appengine.ext import ndb

class StudioClass(ndb.Model):
    recurrence_id = ndb.StringProperty()

    studio_name = ndb.StringProperty()
    source_page = ndb.StringProperty(indexed=False)
    style = ndb.StringProperty(indexed=False)
    teacher = ndb.StringProperty(indexed=False)
    teacher_link = ndb.StringProperty(indexed=False)
    start_time = ndb.DateTimeProperty()
    end_time = ndb.DateTimeProperty(indexed=False)

    auto_categories = ndb.StringProperty(repeated=True)

    latitude = ndb.FloatProperty(indexed=False)
    longitude = ndb.FloatProperty(indexed=False)
    address = ndb.StringProperty(indexed=False)

    scrape_time = ndb.DateTimeProperty(indexed=False)
