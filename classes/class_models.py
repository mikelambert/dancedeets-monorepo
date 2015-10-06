
from google.appengine.ext import ndb

class StudioClass(ndb.Model):
    studio_name = ndb.StringProperty()
    source_page = ndb.StringProperty()
    style = ndb.StringProperty()
    teacher = ndb.StringProperty()
    teacher_link = ndb.StringProperty()
    start_time = ndb.DateTimeProperty(indexed=False)
    end_time = ndb.DateTimeProperty(indexed=False)

    auto_categories = ndb.StringProperty(repeated=True)

    latitude = ndb.FloatProperty()
    longitude = ndb.FloatProperty()

    scrape_time = ndb.DateTimeProperty(indexed=False)
