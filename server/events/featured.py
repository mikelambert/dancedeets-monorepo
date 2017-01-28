import logging
from shapely import geometry

from google.appengine.ext import ndb

MAX_OBJECTS = 100

class FeaturedResult(ndb.Model):
    event_id = ndb.StringProperty()
    json_props = ndb.JsonProperty(indexed=False)

    @property
    def polygon(self):
        return geometry.Polygon(self.json_props['polygon'])

def get_featured_events_for(southwest, northeast):
    if not southwest or not northeast:
        return []

    search_polygon = geometry.Polygon([
        # lat (y), long (x)
        (southwest[0], southwest[1]),
        (southwest[0], northeast[1]),
        (northeast[0], northeast[1]),
        (northeast[0], southwest[1]),
    ])
    featured_results = FeaturedResult.query().fetch(MAX_OBJECTS)
    relevant_featured = [x for x in featured_results if search_polygon.intersects(x.polygon)]
    return [x.event_id for x in relevant_featured]
