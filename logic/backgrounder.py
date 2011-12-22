import urllib

from google.appengine.api import taskqueue

def load_users(user_ids, allow_cache=True, **kwargs):
    allow_cache_arg = (allow_cache and '1' or '0')
    for fb_uid in user_ids:
        taskqueue.add(method='GET', url='/tasks/load_users?'+urllib.urlencode(dict(user_id=fb_uid, user_ids=fb_uid, allow_cache=allow_cache_arg)), queue_name='slow-queue', **kwargs)

def load_events_full(fb_event_ids, allow_cache=True, **kwargs):
    # Only once we've finished loading the raw events do we bother loading any event members
    load_events(fb_event_ids, allow_cache, **kwargs)
    load_event_attending(fb_event_ids, allow_cache, **kwargs)

def load_events(fb_event_ids, allow_cache=True, **kwargs):
    fb_uid = '701004' # Mike Lambert
    task_size = 10
    allow_cache_arg = (allow_cache and '1' or '0')
    for i in range(0, len(fb_event_ids), task_size):
        taskqueue.add(method='GET', url='/tasks/load_events?' + urllib.urlencode(dict(user_id=fb_uid, event_ids=','.join(str(x) for x in fb_event_ids[i:i+task_size]), allow_cache=allow_cache_arg)), queue_name='slow-queue', **kwargs)


def load_event_attending(fb_event_ids, allow_cache=True, **kwargs):
    fb_uid = '701004' # Mike Lambert
    task_size = 10
    allow_cache_arg = (allow_cache and '1' or '0')
    for i in range(0, len(fb_event_ids), task_size):
        taskqueue.add(method='GET', url='/tasks/load_event_attending?'+urllib.urlencode(dict(user_id=fb_uid, event_ids=','.join(str(x) for x in fb_event_ids[i:i+task_size]), allow_cache=allow_cache_arg)), queue_name='slow-queue', **kwargs)

def load_potential_events_for_users(fb_uids, allow_cache=True, **kwargs):
    #OPT: support more than one fbuser context per request in BaseTaskFacebookRequestHandler.initialize()
    task_size = 1
    allow_cache_arg = (allow_cache and '1' or '0')
    for i in range(0, len(fb_uids), task_size):
        taskqueue.add(method='GET', url='/tasks/load_potential_events_for_user?' + urllib.urlencode(dict(user_id=','.join(str(x) for x in fb_uids[i:i+task_size]), user_ids=','.join(str(x) for x in fb_uids[i:i+task_size]), allow_cache=allow_cache_arg)), queue_name='slow-queue', **kwargs)



def load_potential_events_for_friends(user_id, fb_uids, allow_cache=True, **kwargs):
    task_size = 1 # 10 seemed to break things with too-large memory sizes
    allow_cache_arg = (allow_cache and '1' or '0')
    for i in range(0, len(fb_uids), task_size):
        taskqueue.add(method='GET', url='/tasks/load_potential_events_for_user?' + urllib.urlencode(dict(user_id=user_id, user_ids=','.join(str(x) for x in fb_uids[i:i+task_size]), allow_cache=allow_cache_arg)), queue_name='slow-queue', **kwargs)

def update_last_login_time(user_id):
    taskqueue.add(method='GET', url='/tasks/update_last_login_time?user_id=%s' % user_id, queue_name='slow-queue')
