#!/usr/bin/env python

import datetime
import logging
import pickle
import time
import urllib

import facebook
from google.appengine.ext import db
from google.appengine.api import urlfetch
from django.utils import simplejson

class FacebookException(Exception):
    pass

RSVP_EVENTS_FQL = """
SELECT eid, rsvp_status
FROM event_member
WHERE uid = %s
"""

# Not used
RSVP_FUTURE_EVENTS_FQL = """
SELECT eid, rsvp_status
FROM event_member
WHERE eid in 
    (SELECT eid FROM event 
    WHERE eid IN (SELECT eid FROM event_member WHERE uid = %s) 
    AND start_time > '%s' ORDER BY start_time)
"""

ALL_EVENTS_FQL = """
SELECT eid, name, start_time, end_time, host
FROM event 
WHERE eid IN (SELECT eid FROM event_member WHERE uid = %s) 
AND start_time > '%s' 
ORDER BY start_time
"""

class FacebookCachedObject(db.Model):
    ckey = db.StringProperty()
    pickled_dict = db.BlobProperty()

    def pickle_dict(self, obj_dict):
        self.pickled_dict = pickle.dumps(obj_dict, pickle.HIGHEST_PROTOCOL)
        if len(self.pickled_dict) > 1024 * 1024 - 200:
            slogging.error("Pickled dictionary getting too large (%s) for key (%s)", len(self.pickled_dict), self.ckey)
        assert self.pickled_dict

    def unpickled_dict(self):
        assert self.pickled_dict
        return pickle.loads(self.pickled_dict)


class BatchLookup(object):
    OBJECT_USER = 'OBJ_USER'
    OBJECT_EVENT = 'OBJ_EVENT'
    OBJECT_EVENT_MEMBERS = 'OBJ_EVENT_MEMBERS'
    OBJECT_FQL = 'OBJ_FQL'

    def _is_cacheable(self, object_key, this_object):
        fb_uid, object_id, object_type = object_key
        if object_type != self.OBJECT_EVENT:
            return True
        elif    'info' in this_object and this_object['info']['privacy'] == 'OPEN':
            return True
        else:
            return False

    def _get_rpcs(self, object_key):
        fb_uid, object_id, object_type = object_key
        if object_type == self.OBJECT_USER:
            today = time.mktime(datetime.date.today().timetuple()[:9])
            return dict(
                profile=self._fetch_rpc('%s' % object_id),
                friends=self._fetch_rpc('%s/friends' % object_id),
                rsvp_for_events=self._fql_rpc(RSVP_EVENTS_FQL % object_id),
                all_event_info=self._fql_rpc(ALL_EVENTS_FQL % (object_id, today)),
            )
        elif object_type == self.OBJECT_EVENT:
            return dict(
                info=self._fetch_rpc('%s' % object_id),
                picture=self._fetch_rpc('%s/picture' % object_id),
            )
        elif object_type == self.OBJECT_EVENT_MEMBERS:
            return dict(
                attending=self._fetch_rpc('%s/attending' % object_id),
                maybe=self._fetch_rpc('%s/maybe' % object_id),
                declined=self._fetch_rpc('%s/declined' % object_id),
                noreply=self._fetch_rpc('%s/noreply' % object_id),
            )
        elif object_type == self.OBJECT_FQL:
            return dict(fql=self._fql_rpc(object_id))
        else:
            raise Exception("Unknown object type %s" % object_type)

    def __init__(self, fb_uid, fb_graph, allow_cache=True):
        self.fb_uid = fb_uid
        self.fb_graph = fb_graph
        self.allow_cache = allow_cache
        self.object_keys = set()

    def _fql_rpc(self, fql):
        rpc = urlfetch.create_rpc()
        url = "https://api.facebook.com/method/fql.query?%s" % urllib.urlencode(dict(query=fql, access_token=self.fb_graph.access_token, format='json'))
        urlfetch.make_fetch_call(rpc, url)
        return rpc

    def _fetch_rpc(self, path):
        rpc = urlfetch.create_rpc()
        url = "https://graph.facebook.com/%s?access_token=%s" % (path, self.fb_graph.access_token)
        urlfetch.make_fetch_call(rpc, url)
        return rpc

    def _user_key(self, user_id):
        return tuple(str(x) for x in (self.fb_uid, user_id, self.OBJECT_USER))
    def _event_key(self, event_id):
        return tuple(str(x) for x in ('701004', event_id, self.OBJECT_EVENT)) #TODO(lambert): make this a shared constant
    def _event_members_key(self, event_id):
        return tuple(str(x) for x in ('701004', event_id, self.OBJECT_EVENT_MEMBERS))
    def _fql_key(self, fql_query):
        return tuple(str(x) for x in (self.fb_uid, fql_query, self.OBJECT_FQL))

    def _string_key(self, key):
        string_key = '.'.join(str(x).replace('.', '-') for x in key)
        escaped_string_key = string_key.replace('"', '-').replace("'", '-')
        return escaped_string_key

    def _db_delete(key_func):
        def db_delete_func(self, id):
            assert id
            results = FacebookCachedObject.gql('where ckey = ' + self._string_key(key_func(self, id))).fetch(1)
            if results:
                results[0].delete()
        return db_delete_func

    def _db_lookup(key_func):
        def db_lookup_func(self, id):
            assert id
            self.object_keys.add(key_func(self, id))
        return db_lookup_func
        
    def _data_for(key_func):
        def data_for_func(self, id):
            assert id
            return self.objects[key_func(self, id)]
        return data_for_func 
        
    invalidate_user = _db_delete(_user_key)
    invalidate_event = _db_delete(_event_key)
    invalidate_event_members = _db_delete(_event_members_key)
    invalidate_fql = _db_delete(_fql_key)

    lookup_user = _db_lookup(_user_key)
    lookup_event = _db_lookup(_event_key)
    lookup_event_members = _db_lookup(_event_members_key)
    lookup_fql = _db_lookup(_fql_key)

    data_for_user = _data_for(_user_key)
    data_for_event = _data_for(_event_key)
    data_for_event_members = _data_for(_event_members_key)
    data_for_fql = _data_for(_fql_key)

    def _get_objects_from_cache(self, object_keys):
        clauses = [self._string_key(key) for key in object_keys]
        query = 'where ckey in :1'
        object_map = {}
        at_a_time = 30 #TODO(lambert): factor this constant out
        for i in range(0, len(clauses), at_a_time):
            objects = FacebookCachedObject.gql(query, clauses[i:i+at_a_time]).fetch(len(object_keys))
            object_map.update(dict((tuple(o.ckey.split('.')), o.unpickled_dict()) for o in objects))
        logging.info("BatchLookup: get_multi objects: %s", object_map.keys())
        return object_map

    def finish_loading(self):
        if self.allow_cache:
            self.objects = self._get_objects_from_cache(self.object_keys)
        else:
            self.objects = {}
        object_keys_to_lookup = list(set(self.object_keys).difference(self.objects.keys()))
        logging.info("BatchLookup: get_multi missed objects: %s", object_keys_to_lookup)

        unknown_results = list(set(self.objects.keys()).difference(self.object_keys))
        assert not len(unknown_results), "Unknown keys found: %s" % unknown_results

        FB_FETCH_COUNT = 10 # number of objects, each of which may be 1-5 RPCs
        for i in range(0, len(object_keys_to_lookup), FB_FETCH_COUNT):
            fetched_objects = self._fetch_object_keys(object_keys_to_lookup[i:i+FB_FETCH_COUNT])    
            # Always store latest fetched stuff in cache, regardless of self.allow_cache
            self._store_objects_into_cache(fetched_objects)
            self.objects.update(fetched_objects)

    @classmethod
    def _map_rpc_to_data(cls, object_key, object_rpc_name, object_rpc):
        fb_uid, object_id, object_type = object_key
        try:
            result = object_rpc.get_result()
            if result.status_code == 200:
                if object_type == cls.OBJECT_EVENT and object_rpc_name == 'picture':
                    return result.final_url
                else:
                    text = result.content
                    return simplejson.loads(text)
        except urlfetch.DownloadError:
            logging.warning("Error downloading: %s", object_rpc.request.url())
        return None

    def _fetch_object_keys(self, object_keys_to_lookup):
        logging.info("Looking up IDs: %s", object_keys_to_lookup)
        # initiate RPCs
        self.object_keys_to_rpcs = {}
        for object_key in object_keys_to_lookup:
            self.object_keys_to_rpcs[object_key] = self._get_rpcs(object_key)
    
        # fetch RPCs
        fetched_objects = {}
        for object_key, object_rpc_dict in self.object_keys_to_rpcs.iteritems():
            this_object = {}
            object_is_bad = False
            for object_rpc_name, object_rpc in object_rpc_dict.iteritems():
                object_json = self._map_rpc_to_data(object_key, object_rpc_name, object_rpc)
                if object_json:
                    this_object[object_rpc_name] = object_json
                else:
                    object_is_bad = True
            if object_is_bad:
                logging.warning("Failed to complete object: %s, only have keys %s", object_key, this_object.keys())
            else:
                fetched_objects[object_key] = this_object

        return fetched_objects

    def _store_objects_into_cache(self, fetched_objects):
        for object_key, this_object in fetched_objects.iteritems():
            if self._is_cacheable(object_key, this_object):
                obj = FacebookCachedObject()
                obj.ckey = self._string_key(object_key)
                obj.pickle_dict(this_object)
                obj.put()
