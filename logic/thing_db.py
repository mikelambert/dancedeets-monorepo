import datetime
import logging

from google.appengine.ext import db

from mapreduce import control
from logic import event_classifier
from util import fb_mapreduce
from util import properties

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

FIELD_FEED = 'FIELD_FEED' # /feed
FIELD_EVENTS = 'FIELD_EVENTS' # /events
FIELD_INVITES = 'FIELD_INVITES' # fql query on invites for signed-up users


def run_modify_transaction_for_key(key, func):
    def inner_modify():
        s = Source.get_by_key_name(str(key))
        func(s)
        s.put()
    db.run_in_transaction(inner_modify)

def increment_num_all_events(source_id):
    def inc(s):
        s.num_all_events = (s.num_all_events or 0) + 1
    run_modify_transaction_for_key(source_id, inc)

def increment_num_potential_events(source_id):
    def inc(s):
        s.num_potential_events = (s.num_potential_events or 0) + 1
    run_modify_transaction_for_key(source_id, inc)

def increment_num_real_events(source_id):
    def inc(s):
        s.num_real_events = (s.num_real_events or 0) + 1
    run_modify_transaction_for_key(source_id, inc)

def increment_num_false_negatives(source_id):
    def inc(s):
        s.num_false_negatives = (s.num_false_negatives or 0) + 1
    run_modify_transaction_for_key(source_id, inc)

def increment_source_event_counters(source_id, potential_event, all_event, real_event, false_negative):
    def inc(s):
        if potential_event:
            s.num_potential_events += 1
        if all_event:
            s.num_all_events += 1
        if real_event:
            s.num_real_events += 1
        if false_negative:
            s.num_false_negatives += 1
    run_modify_transaction_for_key(source_id, inc)


class Source(db.Model):
    graph_id = property(lambda x: int(x.key().name()))
    graph_type = db.StringProperty(choices=GRAPH_TYPES)

    # cached/derived from fb data
    name = db.StringProperty()
    feed_history_in_seconds = db.IntegerProperty()

    # probably to assume for a given event? rough weighting factor?
    freestyle = db.FloatProperty()
    choreo = db.FloatProperty()

    creating_fb_uid = db.IntegerProperty()
    creation_time = db.DateTimeProperty()
    last_scrape_time = db.DateTimeProperty()

    num_all_events = db.IntegerProperty()
    num_potential_events = db.IntegerProperty()
    num_real_events = db.IntegerProperty()
    num_false_negatives = db.IntegerProperty()

    def fraction_potential_are_real(self, bias=0):
        if self.num_potential_events:
            return (self.num_real_events + bias) / (self.num_potential_events + bias)
        else:
            return 0

    def fraction_real_are_false_negative(self, bias=1):
        if self.num_real_events:
            return (self.num_false_negatives + bias) / (self.num_real_events + bias)
        else:
            return 

    def compute_derived_properties(self, fb_data):
        if fb_data: # only update these when we have feed data
            if 'likes' in fb_data['info']:
                self.graph_type = GRAPH_TYPE_FANPAGE
            elif 'locale' in fb_data['info']:
                self.graph_type = GRAPH_TYPE_PROFILE
            elif 'version' in fb_data['info']:
                self.graph_type = GRAPH_TYPE_GROUP
            elif 'start_time' in fb_data['info']:
                self.graph_type = GRAPH_TYPE_EVENT
            else:
                logging.info("cannot classify id %s", fb_data['info']['id'])

            self.name = fb_data['info']['name']
            feed = fb_data['feed']['data']
            if len(feed):
                dt = datetime.datetime.strptime(feed[-1]['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
                td = datetime.datetime.now() - dt
                total_seconds = td.seconds + td.days * 24 * 3600
                self.feed_history_in_seconds = total_seconds
                logging.info('time delta is %s', self.feed_history_in_seconds)
            else:
                self.feed_history_in_seconds = 0

def link_for_fb_source(data):
    if 'likes' in data['info']:
        return data['info']['link']
    elif 'locale' in data['info']:
        return 'http://www.facebook.com/profile.php?id=%s' % data['info']['id']
    elif 'version' in data['info']:
        return 'http://www.facebook.com/groups/%s/' % data['info']['id']
    elif 'start_time' in data['info']:
        return 'http://www.facebook.com/event.php?eid=%s' % data['info']['id']
    else:
        logging.info("cannot classify id %s", source_id)
        return None

def create_source_for_id(source_id, fb_data):
    source = Source.get_by_key_name(str(source_id)) or Source(key_name=str(source_id))
    source.compute_derived_properties(fb_data)
    logging.info('source %s: %s', source.graph_id, source.name)
    return source

def create_source_from_event(db_event, batch_lookup):
    if not db_event.owner_fb_uid:
        return
    # technically we could check if the object exists in the db, before we bother fetching the feed
    batch_lookup.lookup_thing_feed(db_event.owner_fb_uid)
    batch_lookup.finish_loading()
    thing_feed = batch_lookup.data_for_thing_feed(db_event.owner_fb_uid)
    if not thing_feed['deleted']:
        s = create_source_for_id(db_event.owner_fb_uid, thing_feed)
        s.put()


def map_clean_source_count(s):
    s.num_all_events = 0
        s.num_potential_events = 0
        s.num_real_events = 0
        s.num_false_negatives = 0
    s.put()

def map_count_potential_event(pe):
    batch_lookup = fb_mapreduce.get_batch_lookup()
    batch_lookup.lookup_event(pe.fb_event_id)
    batch_lookup.finish_loading()

    fb_event = batch_lookup.data_for_event(pe.fb_event_id)
    classified_event = event_classifier.get_classified_event(fb_event)

    from events import eventdata
    db_event = eventdata.DBEvent.get_by_key_name(pe.fb_event_id)
    for source_id in pe.source_ids:
        potential_event = classified_event.is_dance_event()
        all_event = True
        real_event = db_event != None
        false_positive = db_event and not classified_event.is_dance_event()
        increment_source_event_counters(source_id,
            potential_event=potential_event,
            all_event=all_event,
            real_event=real_event,
            false_positive=false_positive
        )

def mr_clean_source_counts():
       control.start_map(
                name='clean source counts',
                reader_spec='mapreduce.input_readers.DatastoreInputReader',
                handler_spec='logic.thing_db.map_clean_source_count',
                mapper_parameters={
                        'entity_kind': 'logic.thing_db.Source',
                },
        )

def mr_count_potential_events(batch_lookup):
    fb_mapreduce.start_map(
        batch_lookup=batch_lookup,
        name='count potential events',
        handler_spec='logic.thing_db.map_count_potential_event',
        entity_kind='logic.potential_events.PotentialEvent'
    )
    

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
