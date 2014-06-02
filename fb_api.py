#!/usr/bin/env python

import datetime
import json
import logging
import re
import time
import urllib

import smemcache
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import urlfetch
from google.appengine.runtime import apiproxy_errors

from util import properties

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
AND start_time > %d
ORDER BY start_time
"""

EXTRA_EVENT_INFO_FQL = """
SELECT
pic, pic_big, pic_small,
all_members_count
FROM event WHERE eid = %s
"""

#TODO(lambert): handle these remaps correctly.
# BatchLookup: Error code from FB server: {u'error': {u'message': u'(#21) Page ID 220841031315396 was migrated to page ID 158188404247583.  Please update your API calls to the new ID', u'code': 21, u'type': u'OAuthException'}}
# Ideally by rewriting the Source object in the database, but possibly by just doing a re-fetch and logging an error?
GRAPH_ID_REMAP = {
    '101647263255275': '117377888288248',
    '108494635874217': '166812893357651',
    '112562075471922': '167332856689209',
    '121563467895146': '127089371410',
    '129439737159149': '139100909525053',
    '142052542504615': '8795543578',
    '142651955805981': '112957202049361',
    '152980021402904': '229023767128303',
    '153515311386826': '228698713808146',
    '155538074456503': '220858621293097',
    '169709049709619': '115488250943',
    '198565903508142': '161033353920734',
    '219906611386321': '193343354016721',
    '303593019043':    '192061414205494',

    '134669003249370': '120378378044400',
    '217990961624072': '29521108328',
    '44354622237':     '30126257526',
    '220841031315396': '158188404247583',
    '165676573469238': '122109891223160',
    '67005352515':     '445476182139728',
    '45736510803':     '513468305391251',
    '223302767713782': '142218145854370',
    '68664365769':     '167812006687539',
    '112943642062193': '94011602705',
    '168894369834992': '317110981749490',
    '228698713808146': '194420200587315',
    '115442831913347': '497581470340231',
    '103707696381236': '10584534401',
    '172387586439':    '401542303239789',
    '103554453032103': '142788135887286',
    '141742665877562': '59131295473',
    '46959674140':     '127038517466349',
    '72641970258':     '59338495094',
    '234408413246661': '352623228143594',
    '170236519747412': '196190050417479',
    '9069836604':      '28488697740',
    '89761282368':     '157213997812124',
    '120899531300867': '378519012217676',
    '263041617062892': '168847153303558',
    '53302268242':     '55525483163',
    '181498505227308': '543969075656477',
    '120083644747513': '305265119562421',
    '108525733238':    '154308851266330',
    '257744680973331': '148879681965549',
    '119332748115673': '48316500871',
    '180020735145':    '313372895420224',
    '83801154426':     '285099288276688',
    '90886174292':     '190829851076620',
    '18425960347':     '117281981759100',
    '271739117808':    '119614368234654',
    '270082953009751': '245963785536247',
    '125638706865':    '191409900994517',
    '287903517909454': '100430370000748',
    '192168277503011': '199617943401581',
    '191484907554056': '13615725277',
    '124635797591463': '128833780535514',
    '28319048195':     '121618391364620',
    '282902225114844': '379202402149937',
    '281977221265':    '28488697740',
    '153128621384906': '108101985909667',
    '152954774590':    '198231600203400',
    '152979334829278': '293194630797776',
    '152121181515319': '141532865994761',
    '123348187700270': '435948253167290',
    '151931734832872': '195161637306570',
    '564734940231203': '757777237571421',
    '122965981084973': '343307669113548',
    '125749890837269': '88757994426',
    '234408413246661': '352623228143594',
    '194694550541308': '210897445610087',
    '19374649864':     '567723283290367',
    '228698713808146': '194420200587315',
    '192168277503011': '199617943401581',
    '191484907554056': '13615725277',
    '18425960347':     '117281981759100',
    '181498505227308': '543969075656477',
    '287903517909454': '100430370000748',
    '180464088635168': '735440503139786',
    '180020735145':    '313372895420224',
    '28319048195':     '121618391364620',
    '282902225114844': '379202402149937',
    '281977221265':    '28488697740',
    '271739117808':    '119614368234654',
    '270082953009751': '245963785536247',
    '263041617062892': '168847153303558',
    '172442628317':    '152012341632748',
    '172387586439':    '401542303239789',
    '257744680973331': '148879681965549',
    '170236519747412': '196190050417479',
    '164210266937284': '375239099289684',
    '133532600076563': '108318605914289',
    '132287910140468': '279868624721',
    '131982660207344': '313372895420224',
    '131834369471':    '6007352619',
    '234408413246661': '352623228143594',
    '160960797296629': '9328458887',
    '160221984083382': '375092315924747',
    '130185697047654': '195452550490652',
    '129443898716':    '339859416120941',
    '200584136628031': '125319455969',
    '198696906825':    '146433465403523',
    '196974990348068': '124590784219792',
    '62227967539':     '255426124546095',
    '196335523739252': '306989494110',
    '196190050417479': '109385715812370',
    '19535763049':     '469996149687727',
    '195404911010':    '211852165520939',
    '155474824523352': '439206306171478',
    '125907024161196': '288203754645692',
    '125319455969':    '284343681602486',
    '42940092128':     '434081896663740',
    '423948080967979': '489006677802748',
    '40713522176':     '258896074197385',
    '372275252805402': '393521007395528',
    '349402151754548': '6218579962',
    '348302478524557': '149905811694303',
    '345813708769888': '1433053350262930',
    '343214621345':    '126408574073851',
    '340538328044':    '102443936484511',
    '33488418630':     '45652663704',
    '328113907081':    '439288682800124',
    '310026505698805': '176275919164429',
    '308631409148934': '123788574302723',
    '307851842599555': '445531178891242',
    '304929282890556': '139057796260362',
    '302384576202':    '370045719776599',
    '217186302149':    '429993677084666',
    '216749701737422': '158902407580774',
    '214309541986996': '623349991055209',
    '439206306171478': '183572455374',
}

EMPTY_CAUSE_INSUFFICIENT_PERMISSIONS = 'insufficient_permissions'
EMPTY_CAUSE_DELETED = 'deleted'

#TODO(lambert): use parent_group to find additional sources to scrape
OBJ_EVENT_FIELDS = ('description', 'end_time', 'id', 'location', 'name', 'owner', 'privacy', 'start_time', 'venue', 'cover', 'admins', 'parent_group')

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

def _all_members_count(fb_event, value=None):
    data = fb_event.get('fql_info', {}).get('data')
    if data and data[0].get('all_members_count'):
        if value:
            data[0]['all_members_count'] = value
        else:
            return data[0]['all_members_count']
    else:
        if value:
            raise ValueError()
        return None

def is_public_ish(fb_event):
    return not fb_event['empty'] and (
        fb_event['info'].get('privacy', 'OPEN') == 'OPEN' or
        _all_members_count(fb_event) > 60
    )


class ExpiredOAuthToken(Exception):
    pass
class NoFetchedDataException(Exception):
    pass


class LookupType(object):
    optional_keys = []
    use_access_token = True

    @classmethod
    def url(cls, path, fields=None, **kwargs):
        if fields:
            return '/%s?%s' % (path, urllib.urlencode(dict(fields=','.join(fields), **kwargs)))
        else:
            return '/%s' % path

    @classmethod
    def fql_url(cls, fql):
        return "/fql?%s" % urllib.urlencode(dict(q=fql))

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
        return dict(
            profile=cls.url('%s' % object_id),
        )
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (USERLESS_UID, object_id, 'OBJ_PROFILE')

class LookupUser(LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return dict(
            profile=cls.url('%s' % object_id),
            friends=cls.url('%s/friends' % object_id),
            permissions=cls.url('%s/permissions' % object_id),
            rsvp_for_future_events=cls.url('%s/events?since=yesterday' % object_id),
        )
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fetching_uid, object_id, 'OBJ_USER')

#TODO(lambert): move these LookupType subclasses out of fb_api.py into client code where they belong,
# keeping this file infrastructure and unmodified as we add new features + LookupTypes
class LookupUserEvents(LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        today = int(time.mktime(datetime.date.today().timetuple()[:9]))
        return dict(
            all_event_info=cls.fql_url(ALL_EVENTS_FQL % (object_id, today)),
        )
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fetching_uid, object_id, 'OBJ_USER_EVENTS')

class LookupFriendList(LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return dict(
            friend_list=cls.url('%s/members' % object_id),
        )
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fetching_uid, object_id, 'OBJ_FRIEND_LIST')

class LookupEvent(LookupType):
    optional_keys = ['cover_info']

    @classmethod
    def get_lookups(cls, object_id):
        return dict(
            info=cls.url(object_id, fields=OBJ_EVENT_FIELDS),
            fql_info=cls.fql_url(EXTRA_EVENT_INFO_FQL % (object_id)),
            # Dependent lookup for the image from the info's cover photo id:
            cover_info=cls.url('', fields=['images'], ids='{result=info:$.cover.cover_id}'),
            # Do we really want another FQL call used up, just for this? Maybe wait until we can convert all of fql_info over?
            #pic_big=cls.url('%s/picture?type=small&redirect=false' % object_id, access_token),
        )
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (USERLESS_UID, object_id, 'OBJ_EVENT')

    @classmethod
    def cleanup_data(cls, object_data):
        """NOTE: modifies object_data in-place"""
        object_data = super(LookupEvent, cls).cleanup_data(object_data)
        # So fql_count's all_members_count can be rounded,
        # to save on unnecessary db updates and indexing.
        # Especially as it's only for privacy check comparison to 60
        # So round down to most significant digit:
        amc = _all_members_count(object_data)
        if amc:
            str_amc = str(amc)
            # Yes, this timed faster than math.round and string-manip
            new_amc = int(str_amc[0])*10**(len(str_amc)-1)
            # Set new all_members_count data.
            _all_members_count(object_data, new_amc)
        return object_data

class LookupEventAttending(LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return dict(
            attending=cls.url('%s/attending' % object_id),
        )
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (USERLESS_UID, object_id, 'OBJ_EVENT_ATTENDING')

class LookupEventMembers(LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return dict(
            attending=cls.url('%s/attending' % object_id),
            maybe=cls.url('%s/maybe' % object_id),
            declined=cls.url('%s/declined' % object_id),
            noreply=cls.url('%s/noreply' % object_id),
        )
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (USERLESS_UID, object_id, 'OBJ_EVENT_MEMBERS')

class LookupFQL(LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return dict(
            fql=cls.fql_url(object_id),
        )
    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fetching_uid, object_id, 'OBJ_FQL')

class LookupThingFeed(LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return dict(
            info=cls.url('%s' % object_id),
            feed=cls.url('%s/feed' % object_id),
        )
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
        objects = smemcache.get_multi(cache_key_mapping.keys())
        object_map = dict((cache_key_mapping[k], v) for (k, v) in objects.iteritems())

        # DEBUG!
        #get_size = len(pickle.dumps(objects))
        #logging.info("BatchLookup: memcache get_multi return size: %s", get_size)
        logging.info("BatchLookup: memcache get_multi objects found: %s", objects.keys())
        return object_map

    def save_objects(self, keys_to_objects):
        memcache_set = {}
        for k, v in keys_to_objects.iteritems():
            if self._is_cacheable(k, v):
                cache_key = self.key_to_cache_key(k)
                memcache_set[cache_key] = v
        smemcache.safe_set_memcache(memcache_set, 2*3600)
        return {}

    def invalidate_keys(self, keys):
        cache_keys = [self.key_to_cache_key(key) for key in keys]
        smemcache.delete_multi(cache_keys)

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
            object_map.update(dict((cache_key_mapping[o.key().name()], o.decode_data()) for o in objects if o))
        logging.info("BatchLookup: db lookup objects found: %s", object_map.keys())
        return object_map

    def save_objects(self, keys_to_objects):
        updated_objects = {}
        for object_key, this_object in keys_to_objects.iteritems():
            if not self._is_cacheable(object_key, this_object):
                #TODO(lambert): cache the fact that it's a private-unshowable event somehow? same as deleted events?
                logging.warning("Looked up event %s but is not cacheable.", object_key)
                continue
            try:
                cache_key = self.key_to_cache_key(object_key)
                obj = FacebookCachedObject.get_or_insert(cache_key)
                old_json_data = obj.json_data
                obj.encode_data(this_object)
                if old_json_data != obj.json_data:
                    obj.put()
                    self.db_updates += 1
                    #DEBUG
                    #logging.info("OLD %s", old_json_data)
                    #logging.info("NEW %s", obj.json_data)
                    # Store list of updated objects for later querying
                    updated_objects[object_key] = this_object
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
        if use_access_token:
            post_args = {'batch': json.dumps(batch_list)}
            if use_access_token and self.access_token:
                post_args["access_token"] = self.access_token
            post_args["include_headers"] = False # Don't need to see all the caching headers per response
            post_data = None if post_args is None else urllib.urlencode(post_args)
            rpc = urlfetch.create_rpc(deadline=DEADLINE)
            urlfetch.make_fetch_call(rpc, "https://graph.facebook.com/", post_data, "POST")
        else:
            if len(batch_list) != 1:
                raise ValueError("Cannot do batch calls without an access_token")
            query = batch_list[0]['relative_url']
            rpc = urlfetch.create_rpc(deadline=DEADLINE)
            urlfetch.make_fetch_call(rpc, "https://graph.facebook.com/" + query)
        self.fb_fetches += len(batch_list)
        return rpc

    def _fetch_object_keys(self, object_keys_to_lookup):
        logging.info("BatchLookup: Looking up IDs: %s", object_keys_to_lookup)
        # initiate RPCs
        object_keys_to_rpcs = {}
        for object_key in object_keys_to_lookup:
            cls, oid = break_key(object_key)
            parts_to_urls = cls.get_lookups(oid)
            batch_list = [dict(method='GET', name=part_key, relative_url=url, omit_response_on_success=False) for (part_key, url) in parts_to_urls.iteritems()]
            rpc = self._create_rpc_for_batch(batch_list, cls.use_access_token)
            object_keys_to_rpcs[object_key] = rpc

        # fetch RPCs
        fetched_objects = {}
        for object_key, object_rpc in object_keys_to_rpcs.iteritems():
            cls, oid = break_key(object_key)
            parts_to_urls = cls.get_lookups(oid)
            mini_batch_list = [dict(name=part_key, relative_url=url) for (part_key, url) in parts_to_urls.iteritems()]
            this_object = {}
            this_object['empty'] = None
            object_is_bad = False
            rpc_results = self._map_rpc_to_data(object_rpc)
            if not cls.use_access_token:
                logging.info(rpc_results)
                rpc_results = [dict(code=200, body=json.dumps(rpc_results))]
            if isinstance(rpc_results, list):
                named_results = zip(mini_batch_list, rpc_results)
            else:
                logging.error("Error occurred on response, rpc_results is %s", rpc_results)
                object_is_bad = True
                named_results = []
            for batch_item, result in named_results:
                #TODO(lambert): handle timeouts:
                #https://developers.facebook.com/docs/graph-api/making-multiple-requests/#timeouts
                object_rpc_name = batch_item['name']
                object_result_code = result['code']
                object_json = json.loads(result['body'])
                if object_result_code in [200, 400] and object_json is not None:
                    error_code = None
                    if type(object_json) == dict and ('error_code' in object_json or 'error' in object_json):
                        error_code = object_json.get('error_code', object_json.get('error', {}).get('code', None))
                    if error_code == 100:
                        # This means the event exists, but the current access_token is insufficient to query it
                        this_object['empty'] = EMPTY_CAUSE_INSUFFICIENT_PERMISSIONS
                    elif error_code:
                        logging.error("BatchLookup: Error code from FB server: %s", object_json)

                        # expired/invalidated OAuth token for User objects. We use one OAuth token per BatchLookup, so no use continuing...
                        # we don't trigger on UserEvents objects since those are often optional and we don't want to break on those, or set invalid bits on those (get it from the User failures instead)
                        error_code = object_json.get('error_code')
                        error_type = object_json.get('error', {}).get('type')
                        error_message = object_json.get('error', {}).get('message')
                        if cls == LookupUser and error_type == 'OAuthException':
                            #TODO(lambert): this will probably need to be moved in light of the new fb-batch-query usage
                            raise ExpiredOAuthToken(error_message)
                        object_is_bad = True
                    elif object_json == False:
                        this_object['empty'] = EMPTY_CAUSE_DELETED
                    else:
                        this_object[object_rpc_name] = object_json
                else:
                    logging.warning("Got code %s when requesting %s: %s", object_result_code, batch_item, result)
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
    new_object_id = str(GRAPH_ID_REMAP.get(str(object_id), str(object_id)))
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

    def fetched_data_multi(self, cls, object_ids, only_if_updated=False):
        return [self._fetched_data_single(cls, object_id, only_if_updated) for object_id in object_ids]

    def _fetched_data_single(self, cls, object_id, only_if_updated):
        key = generate_key(cls, object_id)
        if (self.force_updated or
              not only_if_updated or
              (only_if_updated and key in self._db_updated_objects)):
            if key in self._fetched_objects:
                return self._fetched_objects[key]
        # only_if_updated means the caller expects to have some None returns
            if only_if_updated:
                return None
            else:
                raise NoFetchedDataException('Could not find %s' % (key,))

    def get(self, cls, object_id, allow_cache=True):
        self.request(cls, object_id, allow_cache=allow_cache)
        self.batch_fetch()
        return self.fetched_data(cls, object_id)

    def get_multi(self, cls, object_ids, allow_cache=True):
        self.request_multi(cls, object_ids, allow_cache=allow_cache)
        self.batch_fetch()
        return self.fetched_data_multi(cls, object_ids)

    def batch_fetch(self):
        object_map, updated_object_map = self._lookup()
        self._fetched_objects.update(object_map)
        self._db_updated_objects = set(updated_object_map.keys())
        return object_map

    def invalidate(self, cls, object_id):
        self.invalidate(cls, (object_id,))

    def invalidate_multi(self, cls, object_ids):
        self.m.invalidate_keys(cls, object_ids)
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
            if self.allow_memcache_read:
                fetched_objects = self._cleanup_object_map(self.m.fetch_keys(keys))
                if self.resave_to_memcache:
                    self.m.save_objects(fetched_objects)
                if self.debug:
                    logging.info("DEBUG: memcache requested %s keys, returned %s objects", len(keys), len(fetched_objects))
                all_fetched_objects.update(fetched_objects)
                unknown_results = set(fetched_objects).difference(keys)
                if len(unknown_results):
                    logging.error("Unknown keys found: %s", unknown_results)
                keys = set(keys).difference(fetched_objects)

            # DB Read
            if self.debug:
                logging.info("DEBUG: allow_dbcache is %s", self.allow_dbcache)
            if self.allow_dbcache:
                fetched_objects = self._cleanup_object_map(self.db.fetch_keys(keys))
                if self.debug:
                    logging.info("DEBUG: db requested %s keys, returned %s objects", len(keys), len(fetched_objects))
                if self.allow_memcache_write:
                    self.m.save_objects(fetched_objects)
                all_fetched_objects.update(fetched_objects)
                unknown_results = set(fetched_objects).difference(keys)
                if len(unknown_results):
                    logging.error("Unknown keys found: %s", unknown_results)
                keys = set(keys).difference(fetched_objects)

        # Facebook Read
        keys.update(self._object_keys_to_lookup_without_cache)

        fetched_objects = self._cleanup_object_map(self.fb.fetch_keys(keys))
        if self.debug:
            logging.info("DEBUG: fb requested %s keys, returned %s objects", len(keys), len(fetched_objects))
        if self.allow_memcache_write:
            self.m.save_objects(fetched_objects)
        updated_objects = self.db.save_objects(fetched_objects)
        all_fetched_objects.update(fetched_objects)
        unknown_results = set(fetched_objects).difference(keys)
        if len(unknown_results):
            logging.error("Unknown keys found: %s", unknown_results)
        keys = set(keys).difference(fetched_objects)

        if keys:
            logging.error("Couldn't find values for keys: %s", keys)

        self.fb_fetches = self.fb.fb_fetches
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

