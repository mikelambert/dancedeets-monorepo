#!/usr/bin/env python

import datetime
import logging
import pickle
import time
import urllib

import facebook
from google.appengine.api import urlfetch
from django.utils import simplejson
import smemcache

#TODO(lambert): set up a background cron job to refresh events, maybe use appengine data store

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

class BatchLookup(object):
    OBJECT_USER = 'USER'
    OBJECT_EVENT = 'EVENT'
    OBJECT_EVENT_MEMBERS = 'EVENT_MEMBERS'
    OBJECT_FQL = 'FQL'

    def _memcache_key(self, object_key):
        return 'Facebook.%s.%s' % (self.fb_uid, object_key)

    def _is_cacheable(self, object_key, this_object):
        object_id, object_type = object_key
        if object_type != self.OBJECT_EVENT:
            return True
        elif  'info' in this_object and this_object['info']['privacy'] == 'OPEN':
            return True
        else:
            return False

    def _get_rpcs(self, object_key):
        object_id, object_type = object_key
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

    def __init__(self, fb_uid, fb_graph, allow_memcache=True):
        self.fb_uid = fb_uid
        self.fb_graph = fb_graph
        self.allow_memcache = allow_memcache
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

    def invalidate_user(self, user_id):
        assert user_id
        smemcache.delete(self._memcache_key((user_id, self.OBJECT_USER)))

    def invalidate_event(self, event_id):
        assert event_id
        smemcache.delete(self._memcache_key((event_id, self.OBJECT_EVENT)))

    def invalidate_event_members(self, event_id):
        assert event_id
        smemcache.delete(self._memcache_key((event_id, self.OBJECT_EVENT_MEMBERS)))

    def invalidate_fql(self, fql_query):
        assert fql_query
        smemcache.delete(self._memcache_key((fql_query, self.OBJECT_FQL)))

    def lookup_user(self, user_id):
        assert user_id
        self.object_keys.add((user_id, self.OBJECT_USER))

    def lookup_event(self, event_id):
        assert event_id
        self.object_keys.add((event_id, self.OBJECT_EVENT))

    def lookup_event_members(self, event_id):
        assert event_id
        self.object_keys.add((event_id, self.OBJECT_EVENT_MEMBERS))

    def lookup_fql(self, fql_query):
        assert fql_query
        self.object_keys.add((fql_query, self.OBJECT_FQL))

    def data_for_user(self, user_id):
        assert user_id
        return self.objects[(user_id, self.OBJECT_USER)]

    def data_for_event(self, event_id):
        assert event_id
        return self.objects[(event_id, self.OBJECT_EVENT)]

    def data_for_event_members(self, event_id):
        assert event_id
        return self.objects[(event_id, self.OBJECT_EVENT_MEMBERS)]

    def data_for_fql(self, fql_query):
        assert fql_query
        return self.objects[(fql_query, self.OBJECT_FQL)]

    def _get_objects_from_memcache(self, object_keys):
        memcache_keys_to_ids = {}
        memcache_keys_to_object_keys = dict((self._memcache_key(object_key), object_key) for object_key in object_keys)
        memcache_keys_to_objects = smemcache.get_multi(memcache_keys_to_object_keys.keys())

        objects = dict((memcache_keys_to_object_keys[k], o) for (k, o) in memcache_keys_to_objects.iteritems())

        get_size = len(pickle.dumps(memcache_keys_to_objects))
        logging.info("BatchLookup: get_multi return size: %s", get_size)
        logging.info("BatchLookup: get_multi objects: %s", objects.keys())
        return objects

    def finish_loading(self):
        if self.allow_memcache:
            self.objects = self._get_objects_from_memcache(self.object_keys)
            object_keys_to_lookup = list(set(self.object_keys).difference(self.objects.keys()))
            logging.info("BatchLookup: get_multi missed objects: %s", object_keys_to_lookup)
        else:
            object_keys_to_lookup = list(self.object_keys)

        FB_FETCH_COUNT = 10 # number of objects, each of which may be 1-5 RPCs
        for i in range(0, len(object_keys_to_lookup), FB_FETCH_COUNT):
            fetched_objects = self._fetch_object_keys(object_keys_to_lookup[i:i+FB_FETCH_COUNT])    
            # Always store latest fetched stuff in memcache, regardless of self.allow_memcache
            self._store_objects_into_memcache(fetched_objects)
            self.objects.update(fetched_objects)

    @classmethod
    def _map_rpc_to_data(cls, object_key, object_rpc_name, object_rpc):
        object_id, object_type = object_key
        try:
            result = object_rpc.get_result()
            if result.status_code == 200:
                if object_type == cls.OBJECT_EVENT and object_rpc_name == 'picture':
                    return result.final_url
                else:
                    text = result.content
                    return simplejson.loads(text)
        except urlfetch.DownloadError:
            logging.error("Error downloading: %s", object_rpc.request.url())
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
                logging.error("Failed to complete object: %s, only have keys %s", object_key, this_object.keys())
            else:
                fetched_objects[object_key] = this_object

        return fetched_objects

    def _store_objects_into_memcache(self, fetched_objects):
        memcache_set = {}
        for object_key, this_object in fetched_objects.iteritems():
            if self._is_cacheable(object_key, this_object):
                memcache_set[self._memcache_key(object_key)] = this_object

        if memcache_set:
            for (k, v) in memcache_set.iteritems():
                smemcache.set(k, v, smemcache.expiry_with_variance(smemcache.MEMCACHE_EXPIRY, smemcache.MEMCACHE_VARIANCE))
            # Doesn't allow any variation between object expiries
            #smemcache.safe_set_memcache(memcache_set, smemcache.MEMCACHE_EXPIRY)
