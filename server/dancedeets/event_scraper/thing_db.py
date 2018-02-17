import datetime
import json
import logging

from google.appengine.ext import db
from mapreduce import json_util
from mapreduce import mapreduce_pipeline
from mapreduce import operation

from dancedeets.events import eventdata
from dancedeets import fb_api
from dancedeets.loc import gmaps_api
from dancedeets.logic import backgrounder
from dancedeets.util import fb_mapreduce

GRAPH_TYPE_PROFILE = 'GRAPH_TYPE_PROFILE'
GRAPH_TYPE_FANPAGE = 'GRAPH_TYPE_FANPAGE'
GRAPH_TYPE_EVENT = 'GRAPH_TYPE_EVENT'
GRAPH_TYPE_GROUP = 'GRAPH_TYPE_GROUP'

GRAPH_TYPES = [
    GRAPH_TYPE_PROFILE,
    GRAPH_TYPE_FANPAGE,
    GRAPH_TYPE_EVENT,
    GRAPH_TYPE_GROUP,
]

# Start small
# Only set of sources with walls, and only hand-curated sources (or events). not grabbing new peoples yet.

FIELD_FEED = 'FIELD_FEED'  # /feed
FIELD_EVENTS = 'FIELD_EVENTS'  # /events
FIELD_INVITES = 'FIELD_INVITES'  # fql query on invites for signed-up users
FIELD_SEARCH = 'FIELD_SEARCH'  # /search?q=


class Source(db.Model):
    graph_id = property(lambda x: str(x.key().name()))
    graph_type = db.StringProperty(choices=GRAPH_TYPES)

    # cached/derived from fb data
    name = db.StringProperty(indexed=False)
    feed_history_in_seconds = db.IntegerProperty(indexed=False)

    fb_info = json_util.JsonProperty(dict, indexed=False)
    latitude = db.FloatProperty(indexed=False)
    longitude = db.FloatProperty(indexed=False)

    street_dance_related = db.BooleanProperty()

    verticals = db.ListProperty(str, indexed=True)

    # probably to assume for a given event? rough weighting factor?
    # do we want to delete these now?
    freestyle = db.FloatProperty(indexed=False)
    choreo = db.FloatProperty(indexed=False)

    #STR_ID_MIGRATE
    creating_fb_uid = db.IntegerProperty(indexed=False)
    creation_time = db.DateTimeProperty(indexed=False, auto_now_add=True)
    last_scrape_time = db.DateTimeProperty(indexed=False)

    num_all_events = db.IntegerProperty(indexed=False)
    num_potential_events = db.IntegerProperty(indexed=False)
    num_real_events = db.IntegerProperty(indexed=False)
    num_false_negatives = db.IntegerProperty(indexed=False)

    emails = db.ListProperty(str, indexed=True)

    def fraction_potential_are_real(self, bias=1):
        num_real_events = (self.num_real_events or 0) + bias
        num_potential_events = (self.num_potential_events or 0) + bias
        if num_potential_events:
            return 1.0 * num_real_events / num_potential_events
        else:
            return 0

    def fraction_real_are_false_negative(self, bias=1):
        if self.num_real_events:
            #TODO(lambert): figure out why num_false_negatives is None, in particular for source id=107687589275667 even after saving
            num_false_negatives = (self.num_false_negatives or 0) + bias
            num_real_events = (self.num_real_events or 0) + bias
            return 1.0 * num_false_negatives / num_real_events
        else:
            return 0

    def compute_derived_properties(self, fb_source_common, fb_source_data):
        if fb_source_common['empty']:  # only update these when we have feed data
            self.fb_info = {}
        else:
            self.fb_info = fb_source_data['info']  # LookupThing* (and all fb_info dependencies). Only used for /search_pages functionality
            self.graph_type = _type_for_fb_source(fb_source_common)
            if 'name' not in fb_source_common['info']:
                logging.error('cannot find name for fb event data: %s, cannot update source data...', fb_source_common)
                return
            self.name = fb_source_common['info']['name']
            self.emails = fb_source_data['info'].get('emails', [])
            if not self.emails:
                pass  # TODO: trigger basic crawl of website to search for emails
            feed = fb_source_common['feed']['data']
            if len(feed):
                dt = datetime.datetime.strptime(feed[-1]['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
                td = datetime.datetime.now() - dt
                total_seconds = td.seconds + td.days * 24 * 3600
                self.feed_history_in_seconds = total_seconds
                #logging.info('feed time delta is %s', self.feed_history_in_seconds)
            else:
                self.feed_history_in_seconds = 0
            location = fb_source_data['info'].get('location')
            if location:
                if location.get('latitude'):
                    self.latitude = float(location.get('latitude'))
                    self.longitude = float(location.get('longitude'))
                else:
                    component_names = ['street', 'city', 'state', 'zip', 'region', 'country']
                    components = [location.get(x) for x in component_names if location.get(x)]
                    address = ', '.join(components)
                    geocode = gmaps_api.lookup_address(address)
                    if geocode:
                        self.latitude, self.longitude = geocode.latlng()
        #TODO(lambert): at some point we need to calculate all potential events, and all real events, and update the numbers with values from them. and all fake events. we have a problem where a new source gets added, adds in the potential events and/or real events, but doesn't properly tally them all. can fix this one-off, but it's too-late now, and i imagine our data will grow inaccurate over time anyway.


def link_for_fb_source(data):
    if 'link' in data['info']:
        return data['info']['link']
    elif 'version' in data['info']:
        return 'http://www.facebook.com/groups/%s/' % data['info']['id']
    elif 'start_time' in data['info']:
        return 'http://www.facebook.com/events/%s/' % data['info']['id']
    else:
        return 'http://www.facebook.com/%s/' % data['info']['id']


def _type_for_fb_source(fb_source_common):
    source_type = fb_source_common['metadata']['metadata']['type']
    if source_type == 'page':
        return GRAPH_TYPE_FANPAGE
    elif source_type == 'user':
        return GRAPH_TYPE_PROFILE
    elif source_type == 'group':
        return GRAPH_TYPE_GROUP
    elif source_type == 'event':
        return GRAPH_TYPE_EVENT
    else:
        logging.info("cannot classify object type for metadata type %s", source_type)
        return None


def get_lookup_for_graph_type(graph_type):
    if graph_type == GRAPH_TYPE_FANPAGE:
        return fb_api.LookupThingPage
    elif graph_type == GRAPH_TYPE_GROUP:
        return fb_api.LookupThingGroup
    elif graph_type == GRAPH_TYPE_PROFILE:
        return fb_api.LookupThingUser
    else:
        logging.error("cannot find LookupType for graph type %s", graph_type)
        raise ValueError('Unknown graph type %s' % graph_type)


def create_source_from_id(fbl, source_id, verticals=None):
    logging.info('create_source_from_id: %s', source_id)
    if not source_id:
        return None

    # Don't create the source if we already have it
    source = Source.get_by_key_name(source_id)
    if source:
        return source

    original_allow_cache = fbl.allow_cache
    fbl.allow_cache = True
    try:

        # technically we could check if the object exists in the db, before we bother fetching the feed
        fb_source_common = fbl.get(fb_api.LookupThingCommon, source_id)
        if fb_source_common['empty']:
            logging.error('Error loading Common Fields for Source: %s', source_id)
            return None

        if source_id != fb_source_common['info']['id']:
            source_id = fb_source_common['info']['id']
            logging.info('found proper id for source: %s', source_id)

        if not fb_source_common['empty']:
            graph_type = _type_for_fb_source(fb_source_common)
            fb_source_data = fbl.get(get_lookup_for_graph_type(graph_type), source_id)

            source = Source(key_name=source_id)
            logging.info('Getting source for id %s: %s', source.graph_id, source.name)
            new_source = (not source.creation_time)
            source.verticals = verticals or []
            source.compute_derived_properties(fb_source_common, fb_source_data)
            source.put()
            if new_source:
                # It seems some "new" sources are existing sources without a creation_time set, so let's force-set it here
                source.creation_time = datetime.datetime.now()
                backgrounder.load_sources([source_id], fb_uid=fbl.fb_uid)
            return source
        return None
    finally:
        fbl.allow_cache = original_allow_cache


def create_sources_from_event(fbl, db_event):
    logging.info('create_sources_from_event: %s', db_event.id)
    create_source_from_id(fbl, db_event.owner_fb_uid, verticals=db_event.verticals)
    for admin in db_event.admins:
        if admin['id'] != db_event.owner_fb_uid:
            create_source_from_id(fbl, admin['id'], verticals=db_event.verticals)


map_create_sources_from_event = fb_mapreduce.mr_wrap(create_sources_from_event)


def explode_per_source_count(pe):
    db_event = eventdata.DBEvent.get_by_id(pe.fb_event_id)

    is_potential_event = pe.match_score > 0
    real_event = db_event != None
    false_negative = bool(db_event and not is_potential_event)
    result = (is_potential_event, real_event, false_negative)

    for source_id in pe.source_ids_only():
        yield (source_id, json.dumps(result))


def combine_source_count(source_id, counts_to_sum):
    s = Source.get_by_key_name(source_id)
    if not s:
        return

    s.num_all_events = 0
    s.num_potential_events = 0
    s.num_real_events = 0
    s.num_false_negatives = 0

    for result in counts_to_sum:
        (potential_event, real_event, false_negative) = json.loads(result)
        s.num_all_events += 1
        if potential_event:
            s.num_potential_events += 1
        if real_event:
            s.num_real_events += 1
        if false_negative:
            s.num_false_negatives += 1
    yield operation.db.Put(s)


def mr_count_potential_events(fbl, queue):
    mapper_params = {
        'entity_kind': 'dancedeets.event_scraper.potential_events.PotentialEvent',
    }
    mapper_params.update(fb_mapreduce.get_fblookup_params(fbl))
    pipeline = mapreduce_pipeline.MapreducePipeline(
        'clean source counts',
        'dancedeets.event_scraper.thing_db.explode_per_source_count',
        'dancedeets.event_scraper.thing_db.combine_source_count',
        'mapreduce.input_readers.DatastoreInputReader',
        None,
        mapper_params=mapper_params,
    )
    pipeline.start(queue_name=queue)


"""
user:
- invited-events fql (event, if member)
- friends (user, if member)
- events (event)
- wall (event, user, page, group)
- likes (page)
- groups (group)

fanpage:
- wall (event, user, page, group)
- likes (page)
- events (event)
- groups (group)

event:
- wall (event, user, page, group)
- attending (user)
- creator (user)

group:
- wall (event, user, page, group)
- members (user)

Known Dancer Entities (profiles, fan pages, events, groups)
- scrape them for events
- track in each entity, how many events were found on wall, events
- track total-time-of-wall so we know refresh frequency

status:
dance-related, scrape, add everything in here to "maybe" list
maybe-dance-related, scrape but only return high-quality events, don't scrape for anything-but-events
not-dance-related, don't scrape
old (event), no longer scrape, happens after event has passed

status set periodically in all-out-mapreduce
- old events stay old
- sources stay dance-related if manually set
- sources become dance-related if they find dance events via it
- sources become not-dance-related if there are no dance events on it after a month or two? or if number of dancer-friends is <20?

- also want to track how many pages/groups were found via this entity
"""
