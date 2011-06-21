import datetime
import logging

from google.appengine.ext import db
from events import tags
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

BIAS_CHOREO = 'BIAS_CHOREO'
BIAS_FREESTYLE = 'BIAS_FREESTYLE'
BIAS_NONE = 'BIAS_NONE'

FIELD_FEED = 'FIELD_FEED' # /feed
FIELD_EVENTS = 'FIELD_EVENTS' # /events
FIELD_INVITES = 'FIELD_INVITES' # fql query on invites for signed-up users

class Source(db.Model):
    graph_id = property(lambda x: int(x.key().name()))
    graph_type = db.StringProperty(choices=GRAPH_TYPES)

    # cached/derived from fb data
    name = db.StringProperty()
    feed_history_in_seconds = db.IntegerProperty()

    # probably to assume for a given event? rough weighting factor?
    freestyle = db.FloatProperty()
    choreo = db.FloatProperty()

    #events_found_json = db.TextProperty()
    #events_found = properties.json_property(events_found_json)

    def compute_derived_properties(self, fb_data):
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

    def dance_type_bias(self):
        if self.freestyle - self.choreo > 0.2:
            return BIAS_FREESTYLE
        elif self.choreo - self.freestyle > 0.2:
            return BIAS_CHOREO
        else:
            return BIAS_NONE

def source_for_user_id(user_id):
    def _source_for_user_id():
        source = Source.get_or_insert(str(user_id))
        source.graph_type = GRAPH_TYPE_PROFILE
        source.put()
        return source
    return _source_for_user_id()
    #return db.run_in_transaction(_source_for_user_id)

def create_source_for_id(source_id, data, style_type):
    source = Source.get_or_insert(str(source_id))
    if 'likes' in data['info']:
        source.graph_type = GRAPH_TYPE_FANPAGE
    elif 'locale' in data['info']:
        source.graph_type = GRAPH_TYPE_PROFILE
    elif 'version' in data['info']:
        source.graph_type = GRAPH_TYPE_GROUP
    elif 'start_time' in data['info']:
        source.graph_type = GRAPH_TYPE_EVENT
    else:
        logging.info("cannot classify id %s", source_id)

    if not style_type or style_type == tags.CHOREO_EVENT:
        source.choreo = 1.0
    else:
        source.choreo = 0.0
    if not style_type or style_type == tags.FREESTYLE_EVENT:
        source.freestyle = 1.0
    else:
        source.freestyle = 0.0

    source.compute_derived_properties(data)
    logging.info('source %s: %s', source.graph_id, source.name)
    source.put()

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
