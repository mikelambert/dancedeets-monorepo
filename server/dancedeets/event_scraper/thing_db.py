"""
Source entity management for Facebook pages/groups/profiles.

The batch source statistics computation has been migrated to Cloud Run Jobs.
See: dancedeets.jobs.update_source_stats

This module retains:
- Source model: Datastore entity for FB sources
- create_source_from_id: Create/update source from FB ID
- create_sources_from_event: Extract sources from event admins/owners
- Helper functions for FB source type detection
"""
import datetime
import logging

from google.appengine.ext import db
from dancedeets.compat.mapreduce import json_util

from dancedeets import fb_api
from dancedeets.loc import gmaps_api
from dancedeets.logic import backgrounder

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

# Field types for source scraping
FIELD_FEED = 'FIELD_FEED'  # /feed
FIELD_EVENTS = 'FIELD_EVENTS'  # /events
FIELD_INVITES = 'FIELD_INVITES'  # fql query on invites for signed-up users
FIELD_SEARCH = 'FIELD_SEARCH'  # /search?q=


class Source(db.Model):
    """Represents a Facebook source (page, group, profile) for event discovery."""
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

    # Style weighting factors (legacy)
    freestyle = db.FloatProperty(indexed=False)
    choreo = db.FloatProperty(indexed=False)

    #STR_ID_MIGRATE
    creating_fb_uid = db.IntegerProperty(indexed=False)
    creation_time = db.DateTimeProperty(indexed=False, auto_now_add=True)
    last_scrape_time = db.DateTimeProperty(indexed=False)

    # Statistics (updated by Cloud Run Job: update_source_stats)
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
            num_false_negatives = (self.num_false_negatives or 0) + bias
            num_real_events = (self.num_real_events or 0) + bias
            return 1.0 * num_false_negatives / num_real_events
        else:
            return 0

    def compute_derived_properties(self, fb_source_common, fb_source_data):
        if fb_source_common['empty']:  # only update these when we have feed data
            self.fb_info = {}
        else:
            self.fb_info = fb_source_data['info']
            self.graph_type = _type_for_fb_source(fb_source_common)
            if 'name' not in fb_source_common['info']:
                logging.error('cannot find name for fb event data: %s, cannot update source data...', fb_source_common)
                return
            self.name = fb_source_common['info']['name']
            self.emails = fb_source_data['info'].get('emails', [])
            feed = fb_source_common['feed']['data']
            if len(feed):
                dt = datetime.datetime.strptime(feed[-1]['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
                td = datetime.datetime.now() - dt
                total_seconds = td.seconds + td.days * 24 * 3600
                self.feed_history_in_seconds = total_seconds
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


def link_for_fb_source(data):
    """Generate Facebook URL for a source."""
    if 'link' in data['info']:
        return data['info']['link']
    elif 'version' in data['info']:
        return 'http://www.facebook.com/groups/%s/' % data['info']['id']
    elif 'start_time' in data['info']:
        return 'http://www.facebook.com/events/%s/' % data['info']['id']
    else:
        return 'http://www.facebook.com/%s/' % data['info']['id']


def _type_for_fb_source(fb_source_common):
    """Determine graph type from FB metadata."""
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
    """Get the appropriate FB API lookup type for a graph type."""
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
    """Create or update a Source from a Facebook ID."""
    source = create_source_from_id_without_saving(fbl, source_id, verticals=verticals)
    if source:
        new_source = (not source.creation_time)
        source.put()
        if new_source:
            source.creation_time = datetime.datetime.now()
            backgrounder.load_sources([source_id], fb_uid=fbl.fb_uid)
    return source


def create_source_from_id_without_saving(fbl, source_id, verticals=None):
    """Create a Source object without saving to Datastore."""
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
            source.verticals = verticals or []
            source.compute_derived_properties(fb_source_common, fb_source_data)
            return source
        return None
    finally:
        fbl.allow_cache = original_allow_cache


def create_sources_from_event(fbl, db_event):
    """Create Source entities from an event's owner and admins."""
    logging.info('create_sources_from_event: %s', db_event.id)
    create_source_from_id(fbl, db_event.owner_fb_uid, verticals=db_event.verticals)
    for admin in db_event.admins:
        if admin['id'] != db_event.owner_fb_uid:
            create_source_from_id(fbl, admin['id'], verticals=db_event.verticals)
