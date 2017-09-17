import datetime
import logging
import pytz
import random
from shapely import geometry

from google.appengine.ext import ndb

from events import eventdata

MAX_OBJECTS = 100


class FeaturedResult(ndb.Model):
    event_id = ndb.StringProperty()
    json_props = ndb.JsonProperty(indexed=False)

    @property
    def polygon(self):
        return geometry.Polygon(self.json_props['polygon'])

    @property
    def showTitle(self):
        return self.json_props.get('showTitle', True) == True


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
    random.shuffle(relevant_featured)

    featured_events = eventdata.DBEvent.get_by_ids([x.event_id for x in relevant_featured])
    featured_infos = []
    for featured_result, featured_event in zip(relevant_featured, featured_events):
        if featured_event.forced_end_time_with_tz < datetime.datetime.utcnow().replace(tzinfo=pytz.utc):
            logging.info('Discarding featured event in the past: %s', featured_event.id)
            continue
        featured_infos.append({'event': featured_event, 'showTitle': featured_result.showTitle})
    return featured_infos
