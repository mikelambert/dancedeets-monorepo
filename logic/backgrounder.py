import urllib

from google.appengine.api.labs import taskqueue

def email_users(fb_uids, **kwargs):
    """Sends out summary emails of upcoming events to all users. Don't call this unless you really mean it."""
    #OPT: support more than one fbuser context per request in BaseTaskFacebookRequestHandler.initialize()
    task_size = 1
    for i in range(0, len(fb_uids), task_size):
        taskqueue.add(method='GET', url='/tasks/email_user?' + urllib.urlencode(dict(user_id=','.join(str(x) for x in fb_uids[i:i+task_size]))), **kwargs)

def load_users(fb_uids, allow_cache=True, **kwargs):
    #OPT: support more than one fbuser context per request in BaseTaskFacebookRequestHandler.initialize()
    task_size = 1
    allow_cache_arg = (allow_cache and '1' or '0')
    for i in range(0, len(fb_uids), task_size):
        taskqueue.add(method='GET', url='/tasks/load_users?' + urllib.urlencode(dict(user_id=','.join(str(x) for x in fb_uids[i:i+task_size]), user_ids=','.join(str(x) for x in fb_uids[i:i+task_size]), allow_cache=allow_cache_arg)), **kwargs)

def load_events_full(fb_event_ids, allow_cache=True, **kwargs):
    # Only once we've finished loading the raw events do we bother loading any event members
    load_events(fb_event_ids, allow_cache, **kwargs)
    load_event_attending(fb_event_ids, allow_cache, **kwargs)

def load_events(fb_event_ids, allow_cache=True, **kwargs):
    fb_uid = '701004' # Mike Lambert
    task_size = 10
    allow_cache_arg = (allow_cache and '1' or '0')
    for i in range(0, len(fb_event_ids), task_size):
        taskqueue.add(method='GET', url='/tasks/load_events?' + urllib.urlencode(dict(user_id=fb_uid, event_ids=','.join(str(x) for x in fb_event_ids[i:i+task_size]), allow_cache=allow_cache_arg)), **kwargs)

def load_event_attending(fb_event_ids, allow_cache=True, **kwargs):
    fb_uid = '701004' # Mike Lambert
    task_size = 10
    allow_cache_arg = (allow_cache and '1' or '0')
    for i in range(0, len(fb_event_ids), task_size):
        taskqueue.add(method='GET', url='/tasks/load_event_attending?'+urllib.urlencode(dict(user_id=fb_uid, event_ids=','.join(str(x) for x in fb_event_ids[i:i+task_size]), allow_cache=allow_cache_arg)), **kwargs)

def load_potential_events_for_users(fb_uids, allow_cache=True, **kwargs):
    #OPT: support more than one fbuser context per request in BaseTaskFacebookRequestHandler.initialize()
    task_size = 1
    allow_cache_arg = (allow_cache and '1' or '0')
    for i in range(0, len(fb_uids), task_size):
        taskqueue.add(method='GET', url='/tasks/load_potential_events_for_user?' + urllib.urlencode(dict(user_id=','.join(str(x) for x in fb_uids[i:i+task_size]), user_ids=','.join(str(x) for x in fb_uids[i:i+task_size]), allow_cache=allow_cache_arg)), **kwargs)

def load_potential_events_for_friends(user_id, fb_uids, allow_cache=True, **kwargs):
    task_size = 10
    allow_cache_arg = (allow_cache and '1' or '0')
    for i in range(0, len(fb_uids), task_size):
        taskqueue.add(method='GET', url='/tasks/load_potential_events_for_user?' + urllib.urlencode(dict(user_id=user_id, user_ids=','.join(str(x) for x in fb_uids[i:i+task_size]), allow_cache=allow_cache_arg)), **kwargs)

def update_last_login_time(user_id):
    taskqueue.add(method='GET', url='/tasks/update_last_login_time?user_id=%s' % user_id)
