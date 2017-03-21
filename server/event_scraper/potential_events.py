import logging

from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors

from util import dates
from . import thing_db

class DiscoveredEvent(object):
    def __init__(self, fb_event_id, source, source_field, extra_source_id=None):
        self.event_id = fb_event_id
        # still necessary for fraction_are_real_event checks...can we remove dependency?
        self.source = source
        self.source_id = source.graph_id if source else None
        self.source_field = source_field
        self.extra_source_id = extra_source_id

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, ', '.join('%s=%s' % x for x in self.__dict__.iteritems()))

    def _cmprepr(self):
        return (self.event_id, self.source_id, self.source_field, self.extra_source_id)

    def __hash__(self):
        return hash(self._cmprepr())

    def __cmp__(self, other):
        if isinstance(other, DiscoveredEvent):
            return cmp(self._cmprepr(), other._cmprepr())
        else:
            return -1


class PESource(object):
    def __init__(self, id, field):
        self.id = id
        self.field = field

    def copy(self):
        return self.__class__(self.id, self.field)

    def __eq__(self, other):
      return self.id == other.id and self.field == other.field

    def __hash__(self):
      return hash((self.id, self.field))

    def __repr__(self):
        return '%s(**%r)' % (self.__class__.__name__, self.__dict__)

class PotentialEvent(db.Model):
    fb_event_id = property(lambda x: str(x.key().name()))

    language = db.StringProperty(indexed=False)
    looked_at = db.BooleanProperty()
    auto_looked_at = db.BooleanProperty(indexed=False)

    # TODO: Should remove these...but keeping until we fixup all our related queries
    match_score = db.IntegerProperty()
    dance_bias_score = db.FloatProperty(indexed=False)
    non_dance_bias_score = db.FloatProperty(indexed=False)
    should_look_at = db.BooleanProperty()
    show_even_if_no_score = db.BooleanProperty()

    #STR_ID_MIGRATE
    source_ids = db.ListProperty(int)
    source_fields = db.ListProperty(str, indexed=False)

    # This is a representation of FUTURE vs PAST, so we can filter in our mapreduce criteria for relevant future events easily
    past_event = db.BooleanProperty()

    def get_invite_uids(self):
        return [source.id for source in self.sources(thing_db.FIELD_INVITES)]

    def sources(self, source_field=None):
        #STR_ID_MIGRATE
        sources = [PESource(str(id) if id else None, field) for (id, field) in zip(self.source_ids, self.source_fields)]

        if source_field:
            sources = [x for x in sources if x.field == source_field]

        return sources

    def source_ids_only(self):
        return [x.id for x in self.sources() if x.id]

    def set_sources(self, sources):
        source_infos_list = list(sources)
        #STR_ID_MIGRATE
        self.source_ids = [long(x.id or 0) for x in source_infos_list]
        self.source_fields = [x.field for x in source_infos_list]

    def has_discovered(self, discovered_event):
        return self.has_source_with_field(discovered_event.source_id, discovered_event.source_field)

    def has_source_with_field(self, source_id, source_field):
        has_source = False
        for source in self.sources():
            if source.id == source_id and source.field == source_field:
                has_source = True
        return has_source


    def set_past_event(self, fb_event):
        if not fb_event:
            past_event = True
        elif fb_event['empty']:
            past_event = True
        else:
            start_time = dates.parse_fb_start_time(fb_event)
            end_time = dates.parse_fb_end_time(fb_event)
            past_event = (dates.TIME_PAST == dates.event_time_period(start_time, end_time))
        changed = (self.past_event != past_event)
        self.past_event = past_event
        return changed


def _common_potential_event_setup(potential_event):
    # This will get set the first time the potential_event is processed...
    potential_event.set_past_event(False)


def make_potential_event_without_source(fb_event_id):
    def _internal_add_potential_event():
        potential_event = PotentialEvent.get_by_key_name(fb_event_id)
        if not potential_event:
            potential_event = PotentialEvent(key_name=fb_event_id)
            # TODO(lambert): this may re-duplicate this work for potential events that already exist. is this okay or not?
            _common_potential_event_setup(potential_event)
            potential_event.put()
        return potential_event
    try:
        potential_event = db.run_in_transaction(_internal_add_potential_event)
    except apiproxy_errors.CapabilityDisabledError, e:
        logging.error("Error saving potential event %s due to %s", fb_event_id, e)

    return potential_event

def make_potential_event_with_source(discovered):
    fb_event_id = discovered.event_id
    # show all events from a source if enough of them slip through our automatic filters
    if discovered.source is not None:
        show_all_events = discovered.source.fraction_real_are_false_negative() > 0.05 and discovered.source_field != thing_db.FIELD_INVITES # never show all invites, privacy invasion
    else:
        show_all_events = discovered.source_field != thing_db.FIELD_INVITES
    def _internal_add_source_for_event_id():
        potential_event = PotentialEvent.get_by_key_name(fb_event_id) or PotentialEvent(key_name=fb_event_id)
        # If already added, return
        if potential_event.has_source_with_field(discovered.source_id, discovered.source_field):
            return False

        _common_potential_event_setup(potential_event)

        # Sometimes we have a source_field with a zeroed/None-d source_id, so be sure to check on source_field
        if discovered.source_field:
            #STR_ID_MIGRATE
            potential_event.set_sources(potential_event.sources() + [PESource(discovered.source_id or 0, discovered.source_field)])

        logging.info('VTFI %s: Just added source id %s/%s to potential event, and saving', fb_event_id, discovered.source_id, discovered.source_field)

        potential_event.show_even_if_no_score = potential_event.show_even_if_no_score or show_all_events
        potential_event.put()
        return True

    new_source = False
    try:
        new_source = db.run_in_transaction(_internal_add_source_for_event_id)
    except apiproxy_errors.CapabilityDisabledError, e:
        logging.error("Error saving potential event %s due to %s", fb_event_id, e)
    potential_event = PotentialEvent.get_by_key_name(fb_event_id)
    logging.info('VTFI %s: Just loaded potential event %s, now with sources: %s', fb_event_id, fb_event_id, potential_event.sources())

    if new_source and discovered.source_id:
        s = thing_db.Source.get_by_key_name(discovered.source_id)
        s.num_all_events = (s.num_all_events or 0) + 1
        s.put()
    return potential_event

