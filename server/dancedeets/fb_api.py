#!/usr/bin/env python

import datetime
import json
import logging
import random
import re
import urllib.parse
import urllib.request

import requests
from google.cloud import ndb

from dancedeets import facebook
from dancedeets.util import fb_events
from dancedeets.util import memcache
from dancedeets.util import mr
from dancedeets.util import properties
from dancedeets.util import urls

# Comparison of pickle vs json:
# http://kbyanc.blogspot.com/2007/07/python-serializer-benchmarks.html
# http://metaoptimize.com/blog/2009/03/22/fast-deserialization-in-python/
# http://www.peterbe.com/plog/json-pickle-or-marshal
# http://inkdroid.org/journal/2008/10/24/json-vs-pickle/

DEADLINE = 20

EMPTY_CAUSE_INSUFFICIENT_PERMISSIONS = 'insufficient_permissions'
EMPTY_CAUSE_DELETED = 'deleted'

#TODO(lambert): use parent_group to find additional sources to scrape
OBJ_EVENT_FIELDS = (
    'description', 'end_time', 'id', 'name', 'owner', 'type', 'start_time', 'event_times', 'place', 'cover', 'admins', 'parent_group',
    'ticket_uri', 'timezone', 'updated_time', 'attending_count', 'declined_count', 'maybe_count', 'noreply_count', 'is_page_owned',
    'is_canceled'
)
OBJ_EVENT_WALL_FIELDS = ('id', 'created_time', 'updated_time', 'message', 'message_tags', 'from', 'link', 'name', 'picture')

OBJ_USER_FIELDS = ('name', 'email', 'first_name', 'last_name', 'locale', 'gender', 'picture', 'link', 'timezone')

OBJ_SOURCE_COMMON_FIELDS = ('id', 'name', 'link')
OBJ_SOURCE_USER_FIELDS = ('id', 'name', 'updated_time', 'first_name', 'last_name')
OBJ_SOURCE_GROUP_FIELDS = ('id', 'name', 'updated_time', 'cover', 'email', 'description', 'parent', 'privacy', 'icon', 'venue', 'owner')
OBJ_SOURCE_PAGE_FIELDS = (
    'id', 'name', 'cover', 'emails', 'about', 'category', 'category_list', 'current_location', 'hometown', 'general_info', 'likes',
    'location', 'phone', 'username', 'website'
)

USERLESS_UID = '701004'


class FacebookCachedObject(ndb.Model):
    json_data = ndb.TextProperty()
    date_cached = ndb.DateTimeProperty(auto_now=True, indexed=False)

    @property
    def data(self):
        if self.json_data:
            return json.loads(self.json_data)
        return None

    @data.setter
    def data(self, value):
        self.json_data = json.dumps(value) if value else None

    def encode_data(self, obj_dict):
        self.data = obj_dict

    def decode_data(self):
        if not self.json_data:
            self.key.delete()  # hack fix to get these objects purged from the system
        return self.data


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
    version = "v2.9"

    @classmethod
    def url(cls, path, fields=None, **kwargs):
        if path is None:
            raise ValueError('Must pass non-empty path argument')
        if fields:
            if isinstance(fields, str):
                raise ValueError('Must pass in a list to fields: %r' % fields)
            kwargs['fields'] = ','.join(fields)
        if kwargs:
            delimiter = '&' if '?' in path else '?'
            return '/%s/%s%s%s' % (cls.version, path, delimiter, urls.urlencode(kwargs))
        else:
            return '/%s/%s' % (cls.version, path)

    @classmethod
    def fql_url(cls, fql):
        return "/%s/fql?%s" % (cls.version, urls.urlencode(dict(q=fql)))

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        raise NotImplementedError()

    @classmethod
    def get_lookups(cls, object_id):
        raise NotImplementedError()

    @classmethod
    def track_lookup(cls):
        pass

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
    def track_lookup(cls):
        mr.increment('fb-lookups-profile')

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
    def track_lookup(cls):
        mr.increment('fb-lookups-user')

    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('profile', cls.url('%s' % object_id, fields=OBJ_USER_FIELDS)),
            ('friends', cls.url('%s/friends' % object_id)),
            ('permissions', cls.url('%s/permissions' % object_id)),
            ('rsvp_for_future_events', cls.url('%s/events?since=yesterday&fields=id,rsvp_status&limit=3000' % object_id)),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fetching_uid or 'None', object_id, 'OBJ_USER')


#TODO(lambert): move these LookupType subclasses out of fb_api.py into client code where they belong,
# keeping this file infrastructure and unmodified as we add new features + LookupTypes
class LookupUserEvents(LookupType):

    fields = ['id', 'name', 'start_time', 'admins', 'rsvp_status', 'picture']

    @classmethod
    def track_lookup(cls):
        mr.increment('fb-lookups-user-events', 3)

    @classmethod
    def get_lookups(cls, object_id):
        common = 'limit=1000&since=yesterday&fields=%s' % ','.join(cls.fields)
        return [
            ('events', cls.url('%s/events?%s' % (object_id, common))),  # attending and unsure
            ('events_declined', cls.url('%s/events?type=declined&%s' % (object_id, common))),
            ('events_not_replied', cls.url('%s/events?type=not_replied&%s' % (object_id, common))),
        ]

    @classmethod
    def all_events(cls, fb_data):
        try:
            return (fb_data['events']['data'] + fb_data['events_declined']['data'] + fb_data['events_not_replied']['data'] + [])
        except KeyError:
            return fb_data['events']['data']

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fetching_uid or 'None', object_id, 'OBJ_USER_EVENTS')


class LookupEvent(LookupType):
    optional_keys = ['cover_info']

    @classmethod
    def track_lookup(cls):
        mr.increment('fb-lookups-event')

    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('info', cls.url(object_id, fields=OBJ_EVENT_FIELDS)),
            # Dependent lookup for the image from the info's cover photo id:
            ('cover_info', cls.url('', fields=['images', 'width', 'height'], ids='{result=info:$.cover.id}')),
            ('picture', cls.url('%s/picture' % object_id, redirect='false', type='large')),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (USERLESS_UID, object_id, 'OBJ_EVENT')


class LookupEventWall(LookupType):
    @classmethod
    def track_lookup(cls):
        mr.increment('fb-lookups-event-wall')

    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('wall', cls.url('%s/feed' % object_id, limit=1000, fields=OBJ_EVENT_WALL_FIELDS)),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (USERLESS_UID, object_id, 'OBJ_EVENT_WALL')


class LookupEventPageComments(LookupType):
    use_access_token = False

    @classmethod
    def track_lookup(cls):
        mr.increment('fb-lookups-comments')

    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('comments', cls.url('comments/', ids=urls.dd_event_url(object_id))),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (USERLESS_UID, object_id, 'OBJ_EVENTPAGE_COMMENTS')


class LookupEventAttending(LookupType):
    """Gets id and name (for display) for just the attending.

    Used with DBEvents, to aggregate the dance names in the city."""

    @classmethod
    def track_lookup(cls):
        mr.increment('fb-lookups-event-rsvp')

    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('attending', cls.url('%s/attending' % object_id, fields=['id', 'name'], limit='2000')),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (USERLESS_UID, object_id, 'OBJ_EVENT_ATTENDING')


class LookupEventAttendingMaybe(LookupType):
    """Gets id-only (faster) for both attending and maybe.

    Used with PotentialEvents, to check if ids are dance-y."""

    @classmethod
    def track_lookup(cls):
        mr.increment('fb-lookups-event-rsvp', 2)

    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('attending', cls.url('%s/attending' % object_id, fields=['id'], limit='2000')),
            ('maybe', cls.url('%s/maybe' % object_id, fields=['id'], limit='2000')),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (USERLESS_UID, object_id, 'OBJ_EVENT_ATTENDING_MAYBE')


class LookupEventMembers(LookupType):
    @classmethod
    def track_lookup(cls):
        mr.increment('fb-lookups-event-rsvp', 4)

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


class LookupThingCommon(LookupType):
    @classmethod
    def track_lookup(cls):
        mr.increment('fb-lookups-source-feed', 1)

    @classmethod
    def get_lookups(cls, object_id):
        return [
            # TODO: Deprecate and delete this...
            # Can't pass fields=OBJ_SOURCE_FIELDS, because we can't guarantee it has all these fields (groups vs pages vs profiles etc)
            ('info', cls.url('%s' % object_id, fields=OBJ_SOURCE_COMMON_FIELDS)),
            ('metadata', cls.url('%s' % object_id, metadata=1)),
            # We need to use limit=10, otherwise we trigger "Please reduce the amount of data you're asking for, then retry your request"
            # on pages that have a feed full of events.
            ('feed', cls.url('%s/feed' % object_id, fields=['created_time', 'updated_time', 'from', 'link', 'message'], limit=10)),
            ('events', cls.url('%s/events' % object_id, limit=500, fields=['id', 'updated_time'])),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return ('None', object_id, 'OBJ_THING_COMMON')


class LookupThingUser(LookupType):
    @classmethod
    def track_lookup(cls):
        mr.increment('fb-lookups-source', 1)

    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('info', cls.url('%s' % object_id, fields=OBJ_SOURCE_USER_FIELDS)),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return ('None', object_id, 'OBJ_THING_USER')


class LookupThingGroup(LookupType):
    @classmethod
    def track_lookup(cls):
        mr.increment('fb-lookups-source', 1)

    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('info', cls.url('%s' % object_id, fields=OBJ_SOURCE_GROUP_FIELDS)),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return ('None', object_id, 'OBJ_THING_GROUP')


class LookupThingPage(LookupType):
    @classmethod
    def track_lookup(cls):
        mr.increment('fb-lookups-source', 1)

    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('info', cls.url('%s' % object_id, fields=OBJ_SOURCE_PAGE_FIELDS)),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return ('None', object_id, 'OBJ_THING_PAGE')


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
        return tuple(re.sub(r'[."\']', '-', urllib.parse.quote(x.encode('utf-8') if isinstance(x, str) else x) if x else 'None') for x in key)

    def key_to_cache_key(self, key):
        cls, oid = break_key(key)
        fetching_uid = self.fetching_uid
        return self._string_key(cls.cache_key(oid, fetching_uid))

    def _is_cacheable(self, object_key, this_object):
        cls, oid = break_key(object_key)
        #TODO: clean this up with inheritance
        if cls == LookupEvent:
            # intentionally empty object
            if this_object.get('empty'):
                return True
            elif this_object.get('info') and fb_events.is_public_ish(this_object):
                return True
            else:
                return False
        elif cls == LookupUser:
            # Always should be able to get something for a given User.
            # If we don't have it, let's avoid caching, and just retry later.
            if this_object.get('empty'):
                return False
            else:
                return True
        return True


class Memcache(CacheSystem):
    def __init__(self, fetching_uid):
        self.fetching_uid = fetching_uid

    def __repr__(self):
        return 'Memcache(%r)' % self.__dict__

    def fetch_keys(self, keys):
        cache_key_mapping = dict((self.key_to_cache_key(key), key) for key in keys)
        objects = memcache.get_multi(list(cache_key_mapping.keys()))
        object_map = dict((cache_key_mapping[k], v) for (k, v) in objects.items())

        # DEBUG!
        #get_size = len(pickle.dumps(objects))
        #logging.info("BatchLookup: memcache get_multi return size: %s", get_size)
        logging.info("BatchLookup: memcache get_multi objects found: %s", list(objects.keys()))
        return object_map

    def save_objects(self, keys_to_objects):
        if not keys_to_objects:
            return
        memcache_set = {}
        for k, v in keys_to_objects.items():
            if self._is_cacheable(k, v):
                cache_key = self.key_to_cache_key(k)
                memcache_set[cache_key] = v
        memcache.set_multi(memcache_set, 2 * 3600)

    def invalidate_keys(self, keys):
        cache_keys = [self.key_to_cache_key(key) for key in keys]
        memcache.delete_multi(cache_keys)


class DBCache(CacheSystem):
    # Maximum number of entities in a single get_multi call
    MAX_ALLOWABLE_QUERIES = 500

    def __init__(self, fetching_uid):
        self.fetching_uid = fetching_uid
        self.db_updates = 0
        self.oldest_allowed = datetime.datetime.min

    def __repr__(self):
        return 'DBCache(%r)' % self.__dict__

    def fetch_keys(self, keys):
        cache_key_mapping = dict((self.key_to_cache_key(key), key) for key in keys)
        object_map = {}
        max_in_queries = self.MAX_ALLOWABLE_QUERIES
        cache_keys = list(cache_key_mapping.keys())
        for i in range(0, len(cache_keys), max_in_queries):
            batch_keys = [ndb.Key(FacebookCachedObject, k) for k in cache_keys[i:i + max_in_queries]]
            objects = ndb.get_multi(batch_keys)
            for o in objects:
                if o:
                    # Sometimes objects get created without json_data, so we need to manually purge those from our DB and not pass them on to clients
                    if o.json_data:
                        if o.date_cached > self.oldest_allowed:
                            object_map[cache_key_mapping[o.key.string_id()]] = o.decode_data()
                    else:
                        o.key.delete()
        logging.info("BatchLookup: db lookup objects found: %s", list(object_map.keys()))
        return object_map

    def save_objects(self, keys_to_objects):
        cache_keys = [self.key_to_cache_key(object_key) for object_key, this_object in keys_to_objects.items()]
        if cache_keys:
            batch_keys = [ndb.Key(FacebookCachedObject, k) for k in cache_keys]
            existing_objects = ndb.get_multi(batch_keys)
        else:
            existing_objects = []

        db_objects_to_put = []
        for obj, (object_key, this_object) in zip(existing_objects, keys_to_objects.items()):
            if not self._is_cacheable(object_key, this_object):
                #TODO(lambert): cache the fact that it's a private-unshowable event somehow? same as deleted events?
                logging.warning("BatchLookup: Looked up id %s but is not cacheable.", object_key)
                continue
            cache_key = self.key_to_cache_key(object_key)
            if not obj:
                obj = FacebookCachedObject(id=cache_key)
            old_json_data = obj.json_data
            obj.encode_data(this_object)
            if old_json_data != obj.json_data:
                self.db_updates += 1
                db_objects_to_put.append(obj)
        if db_objects_to_put:
            try:
                ndb.put_multi(db_objects_to_put)
            except Exception as e:
                logging.warning('Error saving to datastore: %s', e)

    def invalidate_keys(self, keys):
        cache_keys = [self.key_to_cache_key(key) for key in keys]
        entity_keys = [ndb.Key(FacebookCachedObject, x) for x in cache_keys]
        ndb.delete_multi(entity_keys)


class FBAPI(CacheSystem):
    def __init__(self, access_token_or_list):
        if isinstance(access_token_or_list, list):
            self.access_token_list = access_token_or_list
        else:
            self.access_token_list = [access_token_or_list]
        self.fb_fetches = 0
        self.raise_on_page_redirect = False

    def __repr__(self):
        return 'FBAPI(%r)' % self.__dict__

    def random_access_token(self):
        return random.choice(self.access_token_list)

    def fetch_keys(self, keys):
        FB_FETCH_COUNT = 10  # number of objects, each of which may be 1-5 RPCs
        fetched_objects = {}
        keys = list(keys)
        for i in range(0, len(keys), FB_FETCH_COUNT):
            fetched_objects.update(self._fetch_object_keys(keys[i:i + FB_FETCH_COUNT]))
        return fetched_objects

    def save_objects(self, keys_to_objects):
        raise NotImplementedError("Cannot save anything to FB")

    def invalidate_keys(self, keys):
        raise NotImplementedError("Cannot invalidate anything in FB")

    def get(self, path, args):
        return self.post(path, args, None)

    def post(self, path, args, post_args):
        if not args: args = {}
        token = self.random_access_token()
        if token:
            if post_args is not None:
                post_args["access_token"] = token
            else:
                args["access_token"] = token
        url = "https://graph.facebook.com/" + path + "?" + urls.urlencode(args)
        if post_args:
            response = requests.post(url, data=post_args, timeout=DEADLINE)
        else:
            response = requests.get(url, timeout=DEADLINE)
        return response.json()

    @staticmethod
    def _map_rpc_to_data(object_rpc):
        # object_rpc is now a requests Response or Future
        if hasattr(object_rpc, 'json'):
            # It's a requests Response
            try:
                if object_rpc.status_code != 200:
                    logging.warning("BatchLookup: Error downloading, error code is %s, body is %s", object_rpc.status_code, object_rpc.text)
                if object_rpc.status_code in [200, 400]:
                    return object_rpc.json()
            except requests.exceptions.RequestException as e:
                logging.warning("BatchLookup: Error downloading: %s", e)
        return None

    def _create_rpc_for_batch(self, batch_list, use_access_token):
        post_args = {'batch': json.dumps(batch_list)}
        token = self.random_access_token()
        if use_access_token and token:
            post_args["access_token"] = token
        else:
            post_args["access_token"] = '%s|%s' % (facebook.FACEBOOK_CONFIG['app_id'], facebook.FACEBOOK_CONFIG['secret_key'])
        post_args["include_headers"] = False  # Don't need to see all the caching headers per response
        # Use requests library instead of urlfetch
        rpc = requests.post("https://graph.facebook.com/", data=post_args, timeout=DEADLINE)
        self.fb_fetches += len(batch_list)
        return rpc, token

    def _fetch_object_keys(self, object_keys_to_lookup):
        logging.info("BatchLookup: Fetching IDs from FB: %s", object_keys_to_lookup)
        # initiate RPCs
        object_keys_to_rpcs = {}
        for object_key in object_keys_to_lookup:
            cls, oid = break_key(object_key)
            cls.track_lookup()
            parts_to_urls = cls.get_lookups(oid)
            batch_list = [
                dict(method='GET', name=part_key, relative_url=url, omit_response_on_success=False) for (part_key, url) in parts_to_urls
            ]
            rpc, token = self._create_rpc_for_batch(batch_list, cls.use_access_token)
            object_keys_to_rpcs[object_key] = rpc, token

        # fetch RPCs
        fetched_objects = {}
        for object_key, (object_rpc, object_token) in object_keys_to_rpcs.items():
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
                    logging.warning("Error with expired token: %s", object_token)
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
                try:
                    object_json = json.loads(result['body'])
                except:
                    logging.error('Error parsing result body for %r: %r', batch_item, result)
                    raise
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
                                from dancedeets.event_scraper import thing_db_fixer
                                from dancedeets.util import deferred
                                logging.warning(message)
                                logging.warning("Executing deferred call to migrate to new ID, returning None here.")
                                deferred.defer(thing_db_fixer.function_migrate_thing_to_new_id, self, from_id, to_id)
                        object_is_bad = True
                    elif error_code in [
                        2,  # Temporary API error: An unexpected error has occurred. Please retry your request later.
                        2500,  # Dependent-lookup on non-existing field: Cannot specify an empty identifier.
                    ]:
                        # Handle errors as documented here: https://developers.facebook.com/docs/graph-api/using-graph-api/v2.0#errors
                        logging.warning("BatchLookup: Error code from FB server for %s: %s: %s", object_rpc_name, error_code, object_json)
                        mr.increment('fb-lookups-errors-%s-%s' % (object_rpc_name, error_code))
                        if object_rpc_name not in cls.optional_keys:
                            object_is_bad = True
                    elif error_code:
                        logging.error("BatchLookup: Error code from FB server for %s: %s: %s", object_rpc_name, error_code, object_json)
                        mr.increment('fb-lookups-errors-%s-%s' % (object_rpc_name, error_code))
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
    new_object_id = json.dumps(object_id, sort_keys=True)
    return (cls, new_object_id)


def break_key(key):
    cls, object_id = key
    return (cls, json.loads(object_id))


class FBLookup(object):
    def __init__(self, fb_uid, access_token):
        self._keys_to_fetch = set()
        self.fb_uid = fb_uid
        self.access_token = access_token
        self._fetched_objects = {}
        self._object_keys_to_lookup_without_cache = set()
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

    def __repr__(self):
        keys = set([
            'fb_uid', 'access_token', 'allow_cache', 'allow_memcache_read', 'allow_memcache_write', 'allow_dbcache', 'resave_to_memcache',
            'debug'
        ])
        newdict = dict(kv for kv in self.__dict__.items() if kv[0] in keys)
        return 'FBLookup(%r)' % newdict

    def __getstate__(self):
        d = self.__dict__.copy()
        d['_fetched_objects'] = {}
        return d

    def make_passthrough(self):
        self.m = None
        self.db = None

    def request(self, cls, object_id, allow_cache=True):
        self.request_multi(cls, (object_id,), allow_cache=allow_cache)

    def request_multi(self, cls, object_ids, allow_cache=True):
        for object_id in object_ids:
            if object_id is None:
                raise ValueError('Must pass a non-empty object id')
            key = generate_key(cls, object_id)
            if allow_cache:
                self._keys_to_fetch.add(key)
            else:
                self._object_keys_to_lookup_without_cache.add(key)

    def fetched_data(self, cls, object_id):
        return self._fetched_data_single(cls, object_id)

    def fetched_data_multi(self, cls, object_ids, allow_fail=False):
        return [self._fetched_data_single(cls, object_id, allow_fail=allow_fail) for object_id in object_ids]

    def _fetched_data_single(self, cls, object_id, allow_fail=False):
        key = generate_key(cls, object_id)
        if key in self._fetched_objects:
            return self._fetched_objects[key]
        elif allow_fail:
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
        object_map = self._lookup()
        self._fetched_objects.update(object_map)
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
            self.db.save_objects(fetched_objects)
        all_fetched_objects.update(fetched_objects)
        unknown_results = set(fetched_objects).difference(keys)
        if len(unknown_results):
            logging.error("BatchLookup: Unknown keys found: %s", unknown_results)
        keys = set(keys).difference(fetched_objects)

        if keys:
            logging.warning("BatchLookup: Couldn't find values for keys: %s", keys)

        self.fb_fetches = self.fb.fb_fetches
        self.db_updates = self.db.db_updates if self.db else 0

        # In case we do futher fetches, don't refetch any of these keys
        self._keys_to_fetch = set()
        self._object_keys_to_lookup_without_cache = set()

        return all_fetched_objects

    @staticmethod
    def _cleanup_object_map(object_map):
        """NOTE: modifies object_map in-place"""
        # Clean up objects
        for k, v in object_map.items():
            cls, oid = break_key(k)
            object_map[k] = cls.cleanup_data(v)
        return object_map


class _LookupDebugToken(LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('token', cls.url('debug_token', input_token=object_id)),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        raise Exception("Should not cache access token debug data")


def lookup_debug_tokens(access_tokens):
    # We use a prod config here, so we can lookup access tokens from prod apps
    app_fbl = FBLookup(None, facebook._PROD_FACEBOOK_CONFIG['app_access_token'])
    app_fbl.make_passthrough()
    result = app_fbl.get_multi(_LookupDebugToken, access_tokens)
    if result and not result[0]['empty']:
        return result
    else:
        app_fbl = FBLookup(None, facebook.FACEBOOK_CONFIG['app_access_token'])
        app_fbl.make_passthrough()
        return app_fbl.get_multi(_LookupDebugToken, access_tokens)
