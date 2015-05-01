#!/usr/bin/env python

import datetime
import json
import logging
import re
import time
import urllib

import facebook
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.runtime import apiproxy_errors

from util import properties
from util import urls

# Comparison of pickle vs json:
# http://kbyanc.blogspot.com/2007/07/python-serializer-benchmarks.html
# http://metaoptimize.com/blog/2009/03/22/fast-deserialization-in-python/
# http://www.peterbe.com/plog/json-pickle-or-marshal
# http://inkdroid.org/journal/2008/10/24/json-vs-pickle/

DEADLINE = 20

ALL_EVENTS_FQL = """
SELECT eid, name, start_time, end_time, host
FROM event 
WHERE eid IN (SELECT eid FROM event_member WHERE uid = %s) 
AND start_time >= %d
ORDER BY start_time
"""


EMPTY_CAUSE_INSUFFICIENT_PERMISSIONS = 'insufficient_permissions'
EMPTY_CAUSE_DELETED = 'deleted'

#TODO(lambert): use parent_group to find additional sources to scrape
OBJ_EVENT_FIELDS = ('description', 'end_time', 'id', 'location', 'name', 'owner', 'privacy', 'start_time', 'venue', 'cover', 'admins', 'parent_group', 'ticket_uri', 'timezone', 'updated_time', 'is_date_only', 'attending_count', 'declined_count', 'maybe_count', 'noreply_count', 'invited_count')

USERLESS_UID = '701004'

class FacebookCachedObject(db.Model):
    json_data = db.TextProperty()
    data = properties.json_property(json_data)
    date_cached = db.DateTimeProperty(auto_now=True, indexed=False)

    def encode_data(self, obj_dict):
        self.data = obj_dict

    def decode_data(self):
        if not self.json_data:
            self.delete() # hack fix to get these objects purged from the system
        return self.data

def _all_members_count(fb_event):
    # TODO(FB2.0): cleanup!
    data = fb_event.get('fql_info', {}).get('data')
    if data and data[0].get('all_members_count'):
        return data[0]['all_members_count']
    else:
        if 'info' in fb_event and fb_event['info'].get('invited_count'):
            return fb_event['info']['invited_count']
        else:
            return None

def is_public_ish(fb_event):
    # Don't allow SECRET events
    return not fb_event['empty'] and (
        fb_event['info'].get('privacy', 'OPEN') == 'OPEN' or
        (fb_event['info'].get('privacy', 'OPEN') == 'FRIENDS' and
         _all_members_count(fb_event) >= 60) or
        (fb_event['info'].get('privacy', 'OPEN') == 'SECRET' and
         _all_members_count(fb_event) >= 200)
    )


class ExpiredOAuthToken(Exception):
    pass
class NoFetchedDataException(Exception):
    pass
class PageRedirectException(Exception):
    def __init__(self, from_id, to_id):
        self.from_id = from_id
        self.to_id = to_id


class LookupType(object):
    optional_keys = []
    use_access_token = True
    version = "v2.2"

    @classmethod
    def url(cls, path, fields=None, **kwargs):
        if fields:
            return '/%s/%s?%s' % (cls.version, path, urllib.urlencode(dict(fields=','.join(fields), **kwargs)))
        else:
            return '/%s/%s' % (cls.version, path)

    @classmethod
    def fql_url(cls, fql):
        return "/%s/fql?%s" % (cls.version, urllib.urlencode(dict(q=fql)))

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        raise NotImplementedError()

    @classmethod
    def get_lookups(cls, object_id):
        raise NotImplementedError()

    @classmethod
    def cleanup_data(cls, object_data):
        """NOTE: modifies object_data in-place"""
        # Backwards-compatibility support for old objects lingering around
        if 'empty' not in object_data:
            object_data['empty'] = object_data.get('deleted') and EMPTY_CAUSE_DELETED or None
        return object_data

class LookupProfile(LookupType):
    use_access_token = False

    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('profile', cls.url('%s' % object_id)),
        ]
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (USERLESS_UID, object_id, 'OBJ_PROFILE')

class LookupUser(LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('profile', cls.url('%s' % object_id)),
            ('friends', cls.url('%s/friends' % object_id)),
            ('permissions', cls.url('%s/permissions' % object_id)),
            ('rsvp_for_future_events', cls.url('%s/events?since=yesterday' % object_id)),
        ]
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fetching_uid, object_id, 'OBJ_USER')

#TODO(lambert): move these LookupType subclasses out of fb_api.py into client code where they belong,
# keeping this file infrastructure and unmodified as we add new features + LookupTypes
class LookupUserEvents(LookupType):
    version = "v2.0" # Using FQL for now, need to migrate off to hit 2.1

    @classmethod
    def get_lookups(cls, object_id):
        today = int(time.mktime(datetime.date.today().timetuple()[:9]))
        return [
            # Going to have to convert this over to /<object_id>/events
            # when we want to hit v2.1 or v2.2 (v2.0 works though).
            # Will require downstream changes on eid-vs-id.
            ('all_event_info', cls.fql_url(ALL_EVENTS_FQL % (object_id, today))),
        ]
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fetching_uid, object_id, 'OBJ_USER_EVENTS')

class LookupEvent(LookupType):
    optional_keys = ['cover_info']

    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('info', cls.url(object_id, fields=OBJ_EVENT_FIELDS)),
            # Dependent lookup for the image from the info's cover photo id:
            ('cover_info', cls.url('', fields=['images'], ids='{result=info:$.cover.cover_id}')),
            ('picture', cls.url('%s/picture?redirect=false&type=large' % object_id)),
        ]
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (USERLESS_UID, object_id, 'OBJ_EVENT')

class LookupEventPageComments(LookupType):
    use_access_token = False

    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('comments', cls.url('/comments/?ids=%s' % urls.fb_event_url(object_id))),
        ]
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (USERLESS_UID, object_id, 'OBJ_EVENTPAGE_COMMENTS')

class LookupEventAttending(LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('attending', cls.url('%s/attending' % object_id)),
        ]
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (USERLESS_UID, object_id, 'OBJ_EVENT_ATTENDING')

class LookupEventMembers(LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('attending', cls.url('%s/attending' % object_id)),
            ('maybe', cls.url('%s/maybe' % object_id)),
            ('declined', cls.url('%s/declined' % object_id)),
            ('noreply', cls.url('%s/noreply' % object_id)),
        ]
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (USERLESS_UID, object_id, 'OBJ_EVENT_MEMBERS')

class LookupThingFeed(LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('info', cls.url('%s' % object_id)),
            ('feed', cls.url('%s/feed' % object_id)),
            ('events', cls.url('%s/events' % object_id)),
        ]
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fetching_uid, object_id, 'OBJ_THING_FEED')

class CacheSystem(object):
    def fetch_keys(self, keys):
        raise NotImplementedError()
    def save_objects(self, keys_to_objects):
        raise NotImplementedError()
    def invalidate_keys(self, keys):
        raise NotImplementedError()

    def _string_key(self, key):
        return '.'.join(self._normalize_key(key))

    def _normalize_key(self, key):
        return tuple(re.sub(r'[."\']', '-', str(x)) for x in key)

    def key_to_cache_key(self, key):
        cls, oid = break_key(key)
        fetching_uid = self.fetching_uid
        return self._string_key(cls.cache_key(oid, fetching_uid))

    def _is_cacheable(self, object_key, this_object):
        cls, oid = break_key(object_key)
        #TODO: clean this up with inheritance
        if cls != LookupEvent:
            return True
        # intentionally empty object
        elif this_object.get('empty'):
            return True
        elif this_object.get('info') and is_public_ish(this_object):
            return True
        else:
            return False


class Memcache(CacheSystem):
    def __init__(self, fetching_uid):
        self.fetching_uid = fetching_uid

    def fetch_keys(self, keys):
        cache_key_mapping = dict((self.key_to_cache_key(key), key) for key in keys)
        objects = memcache.get_multi(cache_key_mapping.keys())
        object_map = dict((cache_key_mapping[k], v) for (k, v) in objects.iteritems())

        # DEBUG!
        #get_size = len(pickle.dumps(objects))
        #logging.info("BatchLookup: memcache get_multi return size: %s", get_size)
        logging.info("BatchLookup: memcache get_multi objects found: %s", objects.keys())
        return object_map

    def save_objects(self, keys_to_objects):
        if not keys_to_objects:
            return
        memcache_set = {}
        for k, v in keys_to_objects.iteritems():
            if self._is_cacheable(k, v):
                cache_key = self.key_to_cache_key(k)
                memcache_set[cache_key] = v
        memcache.set_multi(memcache_set, 2*3600)
        return {}

    def invalidate_keys(self, keys):
        cache_keys = [self.key_to_cache_key(key) for key in keys]
        memcache.delete_multi(cache_keys)

class DBCache(CacheSystem):
    def __init__(self, fetching_uid):
        self.fetching_uid = fetching_uid
        self.db_updates = 0

    def fetch_keys(self, keys):
        cache_key_mapping = dict((self.key_to_cache_key(key), key) for key in keys)
        object_map = {}
        max_in_queries = datastore.MAX_ALLOWABLE_QUERIES
        cache_keys = cache_key_mapping.keys()
        for i in range(0, len(cache_keys), max_in_queries):
            objects = FacebookCachedObject.get_by_key_name(cache_keys[i:i+max_in_queries])
            for o in objects:
                if o:
                    # Sometimes objects get created without json_data, so we need to manually purge those from our DB and not pass them on to clients
                    if o.json_data:
                        object_map[cache_key_mapping[o.key().name()]] = o.decode_data()
                    else:
                        o.delete()
        logging.info("BatchLookup: db lookup objects found: %s", object_map.keys())
        return object_map

    def save_objects(self, keys_to_objects):
        updated_objects = {}
        cache_keys = [self.key_to_cache_key(object_key) for object_key, this_object in keys_to_objects.iteritems()]
        if cache_keys:
            existing_objects = FacebookCachedObject.get_by_key_name(cache_keys)
        else:
            existing_objects = []

        db_objects_to_put = []
        for obj, (object_key, this_object) in zip(existing_objects, keys_to_objects.iteritems()):
            if not self._is_cacheable(object_key, this_object):
                #TODO(lambert): cache the fact that it's a private-unshowable event somehow? same as deleted events?
                logging.warning("BatchLookup: Looked up event %s but is not cacheable.", object_key)
                continue
            cache_key = self.key_to_cache_key(object_key)
            if not obj:
                obj = FacebookCachedObject(key_name=cache_key)
            old_json_data = obj.json_data
            obj.encode_data(this_object)
            if old_json_data != obj.json_data:
                self.db_updates += 1
                db_objects_to_put.append(obj)
                #DEBUG
                #logging.info("OLD %s", old_json_data)
                #logging.info("NEW %s", obj.json_data)
                # Store list of updated objects for later querying
                updated_objects[object_key] = this_object
        if db_objects_to_put:
            try:
                db.put(db_objects_to_put)
            except apiproxy_errors.CapabilityDisabledError:
                pass
        return updated_objects

    def invalidate_keys(self, keys):
        cache_keys = [self.key_to_cache_key(key) for key in keys]
        results = FacebookCachedObject.get_by_key_name(cache_keys)
        for result in results:
            result.delete()


class FBAPI(CacheSystem):
    def __init__(self, access_token):
        self.access_token = access_token
        self.fb_fetches = 0
        self.raise_on_page_redirect = False

    def fetch_keys(self, keys):
        FB_FETCH_COUNT = 10 # number of objects, each of which may be 1-5 RPCs
        fetched_objects = {}
        keys = list(keys)
        for i in range(0, len(keys), FB_FETCH_COUNT):
            fetched_objects.update(self._fetch_object_keys(keys[i:i+FB_FETCH_COUNT]))
        return fetched_objects

    def save_objects(self, keys_to_objects):
        raise NotImplementedError("Cannot save anything to FB")
    def invalidate_keys(self, keys):
        raise NotImplementedError("Cannot invalidate anything in FB")

    def post(self, path, args, post_args):
        if not args: args = {}
        if self.access_token:
            if post_args is not None:
                post_args["access_token"] = self.access_token
            else:
                args["access_token"] = self.access_token
        post_data = None if post_args is None else urllib.urlencode(post_args)
        f = urllib.urlopen(
                "https://graph.facebook.com/" + path + "?" +
                urllib.urlencode(args), post_data)
        result = f.read()
        return result

    @staticmethod
    def _map_rpc_to_data(object_rpc):
        try:
            result = object_rpc.get_result()
            if result.status_code != 200:
                logging.warning("BatchLookup: Error downloading, error code is %s, body is %s", result.status_code, result.content)
            if result.status_code in [200, 400]:
                text = result.content
                return json.loads(text)
        except urlfetch.DownloadError, e:
            logging.warning("BatchLookup: Error downloading: %s", e)
        return None

    def _create_rpc_for_batch(self, batch_list, use_access_token):
        post_args = {'batch': json.dumps(batch_list)}
        if use_access_token and self.access_token:
            post_args["access_token"] = self.access_token
        else:
            post_args["access_token"] = '%s|%s' % (facebook.FACEBOOK_CONFIG['app_id'], facebook.FACEBOOK_CONFIG['secret_key'])
        post_args["include_headers"] = False # Don't need to see all the caching headers per response
        post_data = None if post_args is None else urllib.urlencode(post_args)
        rpc = urlfetch.create_rpc(deadline=DEADLINE)
        urlfetch.make_fetch_call(rpc, "https://graph.facebook.com/", post_data, "POST")
        self.fb_fetches += len(batch_list)
        return rpc

    def _fetch_object_keys(self, object_keys_to_lookup):
        logging.info("BatchLookup: Fetching IDs from FB: %s", object_keys_to_lookup)
        # initiate RPCs
        object_keys_to_rpcs = {}
        for object_key in object_keys_to_lookup:
            cls, oid = break_key(object_key)
            parts_to_urls = cls.get_lookups(oid)
            batch_list = [dict(method='GET', name=part_key, relative_url=url, omit_response_on_success=False) for (part_key, url) in parts_to_urls]
            rpc = self._create_rpc_for_batch(batch_list, cls.use_access_token)
            object_keys_to_rpcs[object_key] = rpc

        # fetch RPCs
        fetched_objects = {}
        for object_key, object_rpc in object_keys_to_rpcs.iteritems():
            cls, oid = break_key(object_key)
            parts_to_urls = cls.get_lookups(oid)
            mini_batch_list = [dict(name=part_key, relative_url=url) for (part_key, url) in parts_to_urls]
            this_object = {}
            this_object['empty'] = None
            object_is_bad = False
            rpc_results = self._map_rpc_to_data(object_rpc)
            if isinstance(rpc_results, list):
                named_results = zip(mini_batch_list, rpc_results)
            elif rpc_results is None:
                logging.warning("BatchLookup: Has empty rpc_results, perhaps due to URL fetch timeout")
                object_is_bad = True
                named_results = []
            else:
                error_code = rpc_results.get('error', {}).get('code')
                error_type = rpc_results.get('error', {}).get('type')
                error_message = rpc_results.get('error', {}).get('message')
                # expired/invalidated OAuth token for User objects. We use one OAuth token per BatchLookup, so no use continuing...
                # we don't trigger on UserEvents objects since those are often optional and we don't want to break on those, or set invalid bits on those (get it from the User failures instead)
                if error_code == 190 and error_type == 'OAuthException':
                    raise ExpiredOAuthToken(error_message)
                logging.error("BatchLookup: Error occurred on response, rpc_results is %s", rpc_results)
                object_is_bad = True
                named_results = []
            for batch_item, result in named_results:
                object_rpc_name = batch_item['name']
                if result is None:
                    logging.warning("BatchLookup: Got timeout when requesting %s", batch_item)
                    if object_rpc_name not in cls.optional_keys:
                        object_is_bad = True
                    continue
                object_result_code = result['code']
                object_json = json.loads(result['body'])
                if object_result_code in [200, 400] and object_json is not None:
                    error_code = None
                    if type(object_json) == dict and ('error_code' in object_json or 'error' in object_json):
                        error_code = object_json.get('error_code', object_json.get('error', {}).get('code', None))
                    if error_code == 100:
                        # This means the event exists, but the current access_token is insufficient to query it
                        this_object['empty'] = EMPTY_CAUSE_INSUFFICIENT_PERMISSIONS
                    elif error_code == 21:
                        message = object_json['error']['message']
                        # Facebook gave us a huge hack when they decided to rename/merge page ids,
                        # and so we are forced to deal with remapping by parsing strings at this lowest level.
                        # "Page ID 289919164441106 was migrated to page ID 175608368718.  Please update your API calls to the new ID"
                        # But only do it once per object, so rely on object_is_bad to tell us whether we've been through this before
                        if not object_is_bad and re.search('Page ID \d+ was migrated to page ID \d+.', message):
                            from_id, to_id = re.findall(r'ID (\d+)', message)
                            if self.raise_on_page_redirect:
                                raise PageRedirectException(from_id, to_id)
                            else:
                                from event_scraper import thing_db_fixer
                                from google.appengine.ext import deferred
                                logging.warning(message)
                                logging.warning("Executing deferred call to migrate to new ID, returning None here.")
                                deferred.defer(thing_db_fixer.function_migrate_thing_to_new_id, self, from_id, to_id)
                        object_is_bad = True
                    elif error_code in [
                            2, # Temporary API error: An unexpected error has occurred. Please retry your request later.
                            2500, # Dependent-lookup on non-existing field: Cannot specify an empty identifier.
                        ]:
                        # Handle errors as documented here: https://developers.facebook.com/docs/graph-api/using-graph-api/v2.0#errors
                        logging.warning("BatchLookup: Error code from FB server for %s: %s: %s", object_rpc_name, error_code, object_json)
                        if object_rpc_name not in cls.optional_keys:
                            object_is_bad = True
                    elif error_code:
                        logging.error("BatchLookup: Error code from FB server for %s: %s: %s", object_rpc_name, error_code, object_json)
                        if object_rpc_name not in cls.optional_keys:
                            object_is_bad = True
                    elif object_json == False:
                        this_object['empty'] = EMPTY_CAUSE_DELETED
                    else:
                        this_object[object_rpc_name] = object_json
                else:
                    logging.warning("BatchLookup: Got code %s when requesting %s: %s", object_result_code, batch_item, result)
                    if object_rpc_name not in cls.optional_keys:
                        object_is_bad = True
            if object_is_bad:
                logging.warning("BatchLookup: Failed to complete object: %s, only have keys %s", object_key, this_object.keys())
            else:
                fetched_objects[object_key] = this_object
        return fetched_objects


def generate_key(cls, object_id):
    if isinstance(object_id, (set, list, tuple)):
        raise TypeError("object_id is of incorrect type: %s" % type(object_id))
    new_object_id = str(object_id)
    return (cls, new_object_id)

def break_key(key):
    cls, object_id = key
    return (cls, object_id)

class FBLookup(object):
    def __init__(self, fb_uid, access_token):
        self._keys_to_fetch = set()
        self.fb_uid = fb_uid
        self.access_token = access_token
        self._fetched_objects = {}
        self._db_updated_objects = set()
        self._object_keys_to_lookup_without_cache = set()
        self.force_updated = False
        self.allow_cache = True
        self.allow_memcache_write = True
        self.allow_memcache_read = True
        self.allow_dbcache = True
        # If we fetch objects from memcache, we can save them back into memcache.
        # Useful for keeping objects in cache when we don't care about staleness.
        self.resave_to_memcache = False
        self.m = Memcache(self.fb_uid)
        self.db = DBCache(self.fb_uid)
        self.fb = FBAPI(self.access_token)
        self.debug = False

    def __getstate__(self):
        d = self.__dict__.copy()
        d['_fetched_objects'] = {}
        d['_db_updated_objects'] = set()
        return d

    def make_passthrough(self):
        self.m = None
        self.db = None

    def request(self, cls, object_id, allow_cache=True):
        self.request_multi(cls, (object_id,), allow_cache=allow_cache)
        
    def request_multi(self, cls, object_ids, allow_cache=True):
        for object_id in object_ids:
            key = generate_key(cls, object_id)
            if allow_cache:
                self._keys_to_fetch.add(key)
            else:
                self._object_keys_to_lookup_without_cache.add(key)

    def fetched_data(self, cls, object_id, only_if_updated=False):
        return self._fetched_data_single(cls, object_id, only_if_updated)

    def fetched_data_multi(self, cls, object_ids, only_if_updated=False, allow_fail=False):
        return [self._fetched_data_single(cls, object_id, only_if_updated, allow_fail=allow_fail) for object_id in object_ids]

    def _fetched_data_single(self, cls, object_id, only_if_updated, allow_fail=False):
        key = generate_key(cls, object_id)
        if (self.force_updated or
              not only_if_updated or
              (only_if_updated and key in self._db_updated_objects)):
            if key in self._fetched_objects:
                return self._fetched_objects[key]
            # only_if_updated means the caller expects to have some None returns
            if only_if_updated or allow_fail:
                return None
            else:
                raise NoFetchedDataException('Could not find %s' % (key,))

    def get(self, cls, object_id, allow_cache=True):
        self.request(cls, object_id, allow_cache=allow_cache)
        self.batch_fetch()
        return self.fetched_data(cls, object_id)

    def get_multi(self, cls, object_ids, allow_cache=True, allow_fail=False):
        self.request_multi(cls, object_ids, allow_cache=allow_cache)
        self.batch_fetch()
        return self.fetched_data_multi(cls, object_ids, allow_fail=allow_fail)

    def batch_fetch(self):
        object_map, updated_object_map = self._lookup()
        self._fetched_objects.update(object_map)
        self._db_updated_objects = set(updated_object_map.keys())
        return object_map

    def invalidate(self, cls, object_id):
        self.invalidate(cls, (object_id,))

    def invalidate_multi(self, cls, object_ids):
        if self.m:
            self.m.invalidate_keys(cls, object_ids)
        if self.db:
            self.db.invalidate_keys(cls, object_ids)

    def clear_local_cache(self):
        self._fetched_objects = {}
        
    def _lookup(self):
        keys = self._keys_to_fetch
        all_fetched_objects = {}
        updated_objects = {}
        if self.debug:
            logging.info("DEBUG: allow_cache is %s", self.allow_cache)
        if self.allow_cache:
            # Memcache Read
            if self.debug:
                logging.info("DEBUG: allow_memcache_read is %s", self.allow_memcache_read)
            if self.m and self.allow_memcache_read:
                fetched_objects = self._cleanup_object_map(self.m.fetch_keys(keys))
                if self.resave_to_memcache:
                    self.m.save_objects(fetched_objects)
                if self.debug:
                    logging.info("DEBUG: memcache requested %s keys, returned %s objects", len(keys), len(fetched_objects))
                all_fetched_objects.update(fetched_objects)
                unknown_results = set(fetched_objects).difference(keys)
                if len(unknown_results):
                    logging.error("BatchLookup: Unknown keys found: %s", unknown_results)
                keys = set(keys).difference(fetched_objects)

            # DB Read
            if self.debug:
                logging.info("DEBUG: allow_dbcache is %s", self.allow_dbcache)
            if self.db and self.allow_dbcache:
                fetched_objects = self._cleanup_object_map(self.db.fetch_keys(keys))
                if self.debug:
                    logging.info("DEBUG: db requested %s keys, returned %s objects", len(keys), len(fetched_objects))
                if self.m and self.allow_memcache_write:
                    self.m.save_objects(fetched_objects)
                all_fetched_objects.update(fetched_objects)
                unknown_results = set(fetched_objects).difference(keys)
                if len(unknown_results):
                    logging.error("BatchLookup: Unknown keys found: %s", unknown_results)
                keys = set(keys).difference(fetched_objects)

        # Facebook Read
        keys.update(self._object_keys_to_lookup_without_cache)

        fetched_objects = self._cleanup_object_map(self.fb.fetch_keys(keys))
        if self.debug:
            logging.info("DEBUG: fb requested %s keys, returned %s objects", len(keys), len(fetched_objects))
        if self.m and self.allow_memcache_write:
            self.m.save_objects(fetched_objects)
        if self.db:
            updated_objects = self.db.save_objects(fetched_objects)
        all_fetched_objects.update(fetched_objects)
        unknown_results = set(fetched_objects).difference(keys)
        if len(unknown_results):
            logging.error("BatchLookup: Unknown keys found: %s", unknown_results)
        keys = set(keys).difference(fetched_objects)

        if keys:
            logging.error("BatchLookup: Couldn't find values for keys: %s", keys)

        self.fb_fetches = self.fb.fb_fetches
        if self.db:
            self.db_updates = self.db.db_updates

        # In case we do futher fetches, don't refetch any of these keys
        self._keys_to_fetch = set()
        self._object_keys_to_lookup_without_cache = set()

        return all_fetched_objects, updated_objects

    @staticmethod
    def _cleanup_object_map(object_map):
        """NOTE: modifies object_map in-place"""
        # Clean up objects
        for k, v in object_map.iteritems():
            cls, oid = break_key(k)
            object_map[k] = cls.cleanup_data(v)
        return object_map

