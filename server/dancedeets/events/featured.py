import datetime
import logging
import random
from shapely import geometry

from google.appengine.ext import ndb

from dancedeets.events import eventdata

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

    @property
    def promotionText(self):
        return self.json_props.get('promotionText', None)


def get_featured_events_for(southwest, northeast):

    if not southwest or not northeast:
        testing_featured_results_offline = False
        if testing_featured_results_offline:
            relevant_featured = FeaturedResult.query().fetch(MAX_OBJECTS)
        else:
            relevant_featured = []
    else:
        featured_results = FeaturedResult.query().fetch(MAX_OBJECTS)
        search_polygon = geometry.Polygon([
            # lat (y), long (x)
            (southwest[0], southwest[1]),
            (southwest[0], northeast[1]),
            (northeast[0], northeast[1]),
            (northeast[0], southwest[1]),
        ])
        relevant_featured = [x for x in featured_results if search_polygon.intersects(x.polygon)]
    random.shuffle(relevant_featured)

    featured_events = eventdata.DBEvent.get_by_ids([x.event_id for x in relevant_featured])
    featured_infos = []
    for featured_result, featured_event in zip(relevant_featured, featured_events):
        if featured_event.is_past():
            logging.info('Discarding featured event in the past: %s', featured_event.id)
            continue
        featured_infos.append({
            'event': featured_event,
            'showTitle': featured_result.showTitle,
            'promotionText': featured_result.promotionText,
        })
    return featured_infos
