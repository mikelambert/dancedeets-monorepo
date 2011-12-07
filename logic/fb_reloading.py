import logging

from google.appengine.datastore import datastore_query

from mapreduce import util
from mapreduce import input_readers

from events import eventdata
import fb_api
from logic import email_events
from logic import potential_events
from util import fb_mapreduce

def mr_load_fb_event(batch_lookup):
        fb_mapreduce.start_map(
                batch_lookup=batch_lookup,
                name='Load Events',
                handler_spec='logic.fb_reloading.map_load_fb_event',
                entity_kind='events.eventdata.DBEvent'
        )

def yield_load_fb_event(batch_lookup, db_event):
    logging.info("loading db event %s", db_event.fb_event_id)
    batch_lookup.lookup_event(db_event.fb_event_id)
    batch_lookup.finish_loading()
    try:
        fb_event = batch_lookup.data_for_event(db_event.fb_event_id)
        db_event.make_findable_for(fb_event)
        db_event.put()
    except fb_api.NoFetchedDataException:
        logging.info("No data fetched for event id %s", db_event.fb_event_id)
map_load_fb_event = fb_mapreduce.mr_wrap(yield_load_fb_event)
load_fb_event = fb_mapreduce.nomr_wrap(yield_load_fb_event)


def mr_load_fb_event_attending(batch_lookup):
        fb_mapreduce.start_map(
                batch_lookup=batch_lookup,
                name='Load Event Attending',
                handler_spec='logic.fb_reloading.map_load_fb_event_attending',
                entity_kind='events.eventdata.DBEvent'
        )

def yield_load_fb_event_attending(batch_lookup, db_event):
    batch_lookup.lookup_event_attending(db_event.fb_event_id)
    batch_lookup.finish_loading()
    fb_event_attending = batch_lookup.data_for_event_attending(db_event.fb_event_id)
    db_event.include_attending_summary(fb_event_attending)
    db_event.put()
map_load_fb_event_attending = fb_mapreduce.mr_wrap(yield_load_fb_event_attending)
load_fb_event_attending = fb_mapreduce.nomr_wrap(yield_load_fb_event_attending)


def mr_load_fb_user(batch_lookup):
        fb_mapreduce.start_map(
                batch_lookup=batch_lookup,
                name='Load Users',
                handler_spec='logic.fb_reloading.map_load_fb_user',
                entity_kind='events.users.User',
        )

def yield_load_fb_user(batch_lookup, user):
    if user.expired_oauth_token:
        return
        batch_lookup.lookup_user(user.fb_uid)
    try:
        batch_lookup.finish_loading()
    except fb_api.ExpiredOAuthToken:
        logging.info("Auth token now expired, mark as such.")
        user.expired_oauth_token = True
        user.put()
        return
        fb_user = batch_lookup.data_for_user(user.fb_uid)
    user.compute_derived_properties(fb_user)
    user.put()
map_load_fb_user = fb_mapreduce.mr_user_wrap(yield_load_fb_user)
load_fb_user = fb_mapreduce.nomr_wrap(yield_load_fb_user)

class FilteredInputReader(input_readers.DatastoreInputReader):

    def _iter_key_range(self, k_range):
        cursor = None
        while True:
            query = k_range.make_ascending_query(
                util.for_name(self._entity_kind))
            self.filter_query(query)
            if cursor:
                query.with_cursor(cursor)

            results = query.fetch(limit=self._batch_size)
            if not results:
                break

            for model_instance in results:
                key = model_instance.key()
                yield key, model_instance
            cursor = query.cursor()

    def filter_query(self, query):
        raise NotImplementedError("filter_query() not implemented in %s" % self.__class__)

class FutureEventInputReader(FilteredInputReader):
    def filter_query(self, query):
        query.filter('search_time_period =', eventdata.TIME_FUTURE)

class PastEventInputReader(FilteredInputReader):
    def filter_query(self, query):
        query.filter('search_time_period =', eventdata.TIME_PAST)

def mr_load_past_fb_event(batch_lookup):
        fb_mapreduce.start_map(
                batch_lookup=batch_lookup,
                name='Load Past Events',
                handler_spec='logic.fb_reloading.map_load_fb_event',
                entity_kind='events.eventdata.DBEvent',
        reader_spec='logic.fb_reloading.PastEventInputReader',
        )

def mr_load_future_fb_event(batch_lookup):
        fb_mapreduce.start_map(
                batch_lookup=batch_lookup,
                name='Load Future Events',
                handler_spec='logic.fb_reloading.map_load_fb_event',
                entity_kind='events.eventdata.DBEvent',
        reader_spec='logic.fb_reloading.FutureEventInputReader',
        )

def mr_load_all_fb_event(batch_lookup):
        fb_mapreduce.start_map(
                batch_lookup=batch_lookup,
                name='Load All Events',
                handler_spec='logic.fb_reloading.map_load_fb_event',
                entity_kind='events.eventdata.DBEvent',
        )


def mr_email_user(batch_lookup):
        fb_mapreduce.start_map(
                batch_lookup=batch_lookup,
                name='Email Users',
        #TODO: MOVE
                handler_spec='logic.fb_reloading.map_email_user',
                entity_kind='events.users.User',
        )

#TODO(lambert): do we really want yield on this one?
def yield_email_user(batch_lookup, user):
        batch_lookup.lookup_user(user.fb_uid)
        batch_lookup.lookup_user_events(user.fb_uid)
    try:
        batch_lookup.finish_loading()
    except fb_api.ExpiredOAuthToken:
        logging.info("Auth token now expired, mark as such.")
        user.expired_oauth_token = True
        user.put()
        return None
    return email_events.email_for_user(user, batch_lookup, batch_lookup.fb_graph, should_send=True)
map_email_user = fb_mapreduce.mr_user_wrap(yield_email_user)
email_user = fb_mapreduce.nomr_wrap(yield_email_user)

def mr_load_potential_events(batch_lookup):
        fb_mapreduce.start_map(
                batch_lookup=batch_lookup,
                name='Load Potential Events For Users',
                handler_spec='logic.fb_reloading.map_load_potential_events',
                entity_kind='events.users.User',
        )

def load_potential_events_for_user_id(batch_lookup, user_id):
    batch_lookup.lookup_user_events(user_id)
    batch_lookup.finish_loading()
    potential_events.get_potential_dance_events(batch_lookup, user_id)

def yield_load_potential_events(batch_lookup, user):
    if user.expired_oauth_token:
        return
    load_potential_events_for_user_id(batch_lookup, user.fb_uid)
map_load_potential_events = fb_mapreduce.mr_user_wrap(yield_load_potential_events)
load_potential_events = fb_mapreduce.nomr_wrap(yield_load_potential_events)


