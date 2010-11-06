#!/usr/bin/env python

import datetime
import logging
import time
import urllib

import facebook
import smemcache
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import urlfetch
from google.appengine.runtime import apiproxy_errors
from django.utils import simplejson

# Comparison of pickle vs json:
# http://kbyanc.blogspot.com/2007/07/python-serializer-benchmarks.html
# http://metaoptimize.com/blog/2009/03/22/fast-deserialization-in-python/
# http://www.peterbe.com/plog/json-pickle-or-marshal
# http://inkdroid.org/journal/2008/10/24/json-vs-pickle/

class FacebookException(Exception):
    pass

DEADLINE = 10

# Not used
RSVP_EVENTS_FQL = """
SELECT eid, rsvp_status
FROM event_member
WHERE uid = %s
"""

RSVP_FUTURE_EVENTS_FQL = """
SELECT eid, rsvp_status
FROM event_member
WHERE eid in 
    (SELECT eid FROM event 
    WHERE eid IN (SELECT eid FROM event_member WHERE uid = %s) 
    AND start_time > %d ORDER BY start_time)
"""

ALL_EVENTS_FQL = """
SELECT eid, name, start_time, end_time, host
FROM event 
WHERE eid IN (SELECT eid FROM event_member WHERE uid = %s) 
AND start_time > %d
ORDER BY start_time
"""

class FacebookCachedObject(db.Model):
    json_data = db.TextProperty()

    def encode_data(self, obj_dict):
        self.json_data = simplejson.dumps(obj_dict)
        if len(self.json_data) > 1024 * 1024 - 200:
            logging.error("Encoded dictionary getting too large (%s) for key (%s)", len(self.json_data), self.key().name())
        assert self.json_data, "No json_data for key = %s" % self.key().name()

    def decode_data(self):
        if not self.json_data:
            self.delete() # hack fix to get these objects purged from the system
        assert self.json_data, "No json_data for key = %s" % self.key().name()
        return simplejson.loads(self.json_data)


class BatchLookup(object):
    OBJECT_USER = 'OBJ_USER'
    OBJECT_EVENT = 'OBJ_EVENT'
    OBJECT_EVENT_MEMBERS = 'OBJ_EVENT_MEMBERS'
    OBJECT_FQL = 'OBJ_FQL'

    def _is_cacheable(self, object_key, this_object):
        fb_uid, object_id, object_type = object_key
        if object_type != self.OBJECT_EVENT:
            return True
        elif 'info' in this_object and this_object['deleted']:
            return True
        elif 'info' in this_object and this_object['info'] and this_object['info']['privacy'] == 'OPEN':
            return True
        else:
            return False

    def _get_rpcs(self, object_key):
        fb_uid, object_id, object_type = object_key
        if object_type == self.OBJECT_USER:
            today = int(time.mktime(datetime.date.today().timetuple()[:9]))
            return dict(
                profile=self._fetch_rpc('%s' % object_id),
                friends=self._fetch_rpc('%s/friends' % object_id),
                rsvp_for_events=self._fql_rpc(RSVP_EVENTS_FQL % (object_id)),
                all_event_info=self._fql_rpc(ALL_EVENTS_FQL % (object_id, today)),
            )
        elif object_type == self.OBJECT_EVENT:
            return dict(
                info=self._fetch_rpc('%s' % object_id, use_access_token=False),
                picture=self._fetch_rpc('%s/picture' % object_id, use_access_token=False),
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

    def _fql_rpc(self, fql, use_access_token=True):
        rpc = urlfetch.create_rpc(deadline=DEADLINE)
        url = "https://api.facebook.com/method/fql.query?%s" % urllib.urlencode(dict(query=fql, format='json'))
        if use_access_token:
            url += "&access_token=%s" % self.fb_graph.access_token
        urlfetch.make_fetch_call(rpc, url)
        return rpc

    def _fetch_rpc(self, path, use_access_token=True):
        rpc = urlfetch.create_rpc(deadline=DEADLINE)
        url = "https://graph.facebook.com/%s" % path
        if use_access_token:
            url += "?access_token=%s" % self.fb_graph.access_token
        urlfetch.make_fetch_call(rpc, url)
        return rpc

    def get_userless_id(self):
        return self.fb_uid

    def _user_key(self, user_id):
        return tuple(str(x) for x in (self.fb_uid, user_id, self.OBJECT_USER))
    def _event_key(self, event_id):
        return tuple(str(x) for x in (self.get_userless_id(), event_id, self.OBJECT_EVENT))
    def _event_members_key(self, event_id):
        return tuple(str(x) for x in (self.get_userless_id(), event_id, self.OBJECT_EVENT_MEMBERS))
    def _fql_key(self, fql_query):
        return tuple(str(x) for x in (self.fb_uid, fql_query, self.OBJECT_FQL))

    def _string_key(self, key):
        string_key = '.'.join(str(x).replace('.', '-') for x in key)
        escaped_string_key = string_key.replace('"', '-').replace("'", '-')
        return escaped_string_key

    def _db_delete(key_func):
        def db_delete_func(self, id):
            assert id
            result = FacebookCachedObject.get_by_key_name(self._string_key(key_func(self, id)))
            if result:
                result.delete()
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

    def _get_objects_from_memcache(self, object_keys):
        clauses = [self._string_key(key) for key in object_keys]
        objects = smemcache.get_multi(clauses)
        object_map = dict((tuple(k.split('.')), v) for (k, v) in objects.iteritems())

        # DEBUG!
        #get_size = len(pickle.dumps(objects))
        #logging.info("BatchLookup: memcache get_multi return size: %s", get_size)
        logging.info("BatchLookup: memcache get_multi objects: %s", objects.keys())

        return object_map

    def _get_objects_from_dbcache(self, object_keys):
        clauses = [self._string_key(key) for key in object_keys]
        object_map = {}
        max_in_queries = datastore.MAX_ALLOWABLE_QUERIES
        for i in range(0, len(clauses), max_in_queries):
            objects = FacebookCachedObject.get_by_key_name(clauses[i:i+max_in_queries])
            object_map.update(dict((tuple(o.key().name().split('.')), o.decode_data()) for o in objects if o))
        logging.info("BatchLookup: db get_multi objects: %s", object_map.keys())
        return object_map

    def finish_loading(self):
        self.objects = {}
        object_keys_to_lookup = list(self.object_keys)

        if self.allow_cache:
            if object_keys_to_lookup:
                # lookup from memcache
                memcache_objects = self._get_objects_from_memcache(object_keys_to_lookup)
                self.objects.update(memcache_objects)
                # warn about strange keys we get back
                unknown_results = set(memcache_objects).difference(object_keys_to_lookup)
                assert not len(unknown_results), "Unknown keys found: %s" % unknown_results
                # and fall back for the rest
                object_keys_to_lookup = set(self.object_keys).difference(memcache_objects)

            # fall back to getting the rest from the db cache
            if object_keys_to_lookup:
                db_objects = self._get_objects_from_dbcache(object_keys_to_lookup)
                self.objects.update(db_objects)
                # warn about strange keys we get back
                unknown_results = set(db_objects).difference(object_keys_to_lookup)
                assert not len(unknown_results), "Unknown keys found: %s" % unknown_results
                # and fall back for the rest
                object_keys_to_lookup = set(object_keys_to_lookup).difference(db_objects)

                # Cache in memcache for next time
                if db_objects:
                    self._store_objects_into_memcache(db_objects)

                # Warn about what our get_multi missed
                logging.info("BatchLookup: get_multi missed objects: %s", object_keys_to_lookup)

        object_keys_to_lookup = list(object_keys_to_lookup)
        FB_FETCH_COUNT = 10 # number of objects, each of which may be 1-5 RPCs
        for i in range(0, len(object_keys_to_lookup), FB_FETCH_COUNT):
            fetched_objects = self._fetch_object_keys(object_keys_to_lookup[i:i+FB_FETCH_COUNT])    
            # Always store latest fetched stuff in cache, regardless of self.allow_cache
            self._store_objects_into_dbcache(fetched_objects)
            self._store_objects_into_memcache(fetched_objects)
            self.objects.update(fetched_objects)

    @classmethod
    def _map_rpc_to_data(cls, object_key, object_rpc_name, object_rpc):
        fb_uid, object_id, object_type = object_key
        try:
            result = object_rpc.get_result()
            if object_type == cls.OBJECT_EVENT and object_rpc_name == 'picture':
                return result.final_url
            elif result.status_code == 200:
                text = result.content
                return simplejson.loads(text)
            else:
                logging.error("BatchLookup: Error downloading: %s, error code is %s", object_rpc.request.url(), result.status_code)
        except urlfetch.DownloadError:
            logging.warning("BatchLookup: Error downloading: %s", object_rpc.request.url())
        return None

    def _fetch_object_keys(self, object_keys_to_lookup):
        logging.info("BatchLookup: Looking up IDs: %s", object_keys_to_lookup)
        # initiate RPCs
        self.object_keys_to_rpcs = {}
        for object_key in object_keys_to_lookup:
            self.object_keys_to_rpcs[object_key] = self._get_rpcs(object_key)
    
        # fetch RPCs
        fetched_objects = {}
        for object_key, object_rpc_dict in self.object_keys_to_rpcs.iteritems():
            this_object = {'deleted': False}
            object_is_bad = False
            for object_rpc_name, object_rpc in object_rpc_dict.iteritems():
                object_json = self._map_rpc_to_data(object_key, object_rpc_name, object_rpc)
                if object_json is not None:
                    if type(object_json) == dict and 'error_code' in object_json:
                        logging.error("BatchLookup: Error code from FB server: %s", object_json)
                        object_is_bad = True
                    elif object_json == False:
                        this_object['deleted'] = True
                    else:
                        this_object[object_rpc_name] = object_json
                else:
                    object_is_bad = True
            if object_is_bad:
                logging.warning("BatchLookup: Failed to complete object: %s, only have keys %s", object_key, this_object.keys())
            else:
                fetched_objects[object_key] = this_object
        return fetched_objects

    def _store_objects_into_memcache(self, fetched_objects):
        memcache_set = {}
        for k, v in fetched_objects.iteritems():
            if self._is_cacheable(k, v):
                memcache_set[self._string_key(k)] = v
        smemcache.safe_set_memcache(memcache_set, 2*3600)

    def _store_objects_into_dbcache(self, fetched_objects):
        for object_key, this_object in fetched_objects.iteritems():
            if not self._is_cacheable(object_key, this_object):
                #TODO(lambert): cache the fact that it's a private-unshowable event somehow? same as deleted events?
                logging.error("Looked up event %s but is not cacheable.", object_key)
                continue
            try:
                obj = FacebookCachedObject.get_or_insert(self._string_key(object_key))
                obj.encode_data(this_object)
                obj.put()
            except apiproxy_errors.CapabilityDisabledError:
                pass
        return fetched_objects

class CommonBatchLookup(BatchLookup):
    def get_userless_id(self):
        return '701004'

