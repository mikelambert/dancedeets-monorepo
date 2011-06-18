from google.appengine.ext import db
from util import properties

THING_PROFILE = 'THING_PROFILE',
THING_FANPAGE = 'THING_FANPAGE',
THING_EVENT = 'THING_EVENT',
THING_GROUP = 'THING_GROUP',

THING_TYPES = [
    THING_PROFILE,
    THING_FANPAGE,
    THING_EVENT,
    THING_GROUP,
]

# Start small
# Only set of things with walls, and only hand-curated things (or events). not grabbing new peoples yet.

class Thing(db.Model):
    graph_id = db.StringProperty()
    graph_type = db.StringProperty(choices=THING_TYPES)

    # cached/derived from fb data
    name = db.StringProperty()
    duration_of_wall = db.IntegerProperty()

    # probably to assume for a given event? rough weighting factor?
    freestyle = db.FloatProperty()
    choreo = db.FloatProperty()

    events_found_json = db.TextProperty()
    events_found = properties.json_property(events_found_json)


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
- things stay dance-related if manually set
- things become dance-related if they find dance events via it
- things become not-dance-related if there are no dance events on it after a month or two? or if number of dancer-friends is <20?

- also want to track how many pages/groups were found via this entity
"""
