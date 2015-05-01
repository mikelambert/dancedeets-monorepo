import urllib

from google.appengine.api import taskqueue

# deferred (http://code.google.com/appengine/articles/deferred.html) is useful, but since we map many of these to code that is also called by servlets (for debugging and/or cronjobs), it's not as useful for these:

def load_users(user_ids, allow_cache=True, **kwargs):
    allow_cache_arg = (allow_cache and '1' or '0')
    for fb_uid in user_ids:
        taskqueue.add(method='GET', url='/tasks/load_users?'+urllib.urlencode(dict(user_id=fb_uid, user_ids=fb_uid, allow_cache=allow_cache_arg)), queue_name='slow-queue', **kwargs)

def load_event_attending(fb_event_ids, allow_cache=True, **kwargs):
    fb_uid = '701004' # Mike Lambert
    task_size = 10
    allow_cache_arg = (allow_cache and '1' or '0')
    for i in range(0, len(fb_event_ids), task_size):
        taskqueue.add(method='GET', url='/tasks/load_event_attending?'+urllib.urlencode(dict(user_id=fb_uid, event_ids=','.join(fb_event_ids[i:i+task_size]), allow_cache=allow_cache_arg)), queue_name='slow-queue', **kwargs)

def load_potential_events_for_users(fb_uids, allow_cache=True, **kwargs):
    #OPT: support more than one fbuser context per request in BaseTaskFacebookRequestHandler.initialize()
    task_size = 1
    allow_cache_arg = (allow_cache and '1' or '0')
    for i in range(0, len(fb_uids), task_size):
        taskqueue.add(method='GET', url='/tasks/load_potential_events_for_user?' + urllib.urlencode(dict(user_id=','.join(fb_uids[i:i+task_size]), user_ids=','.join(fb_uids[i:i+task_size]), allow_cache=allow_cache_arg)), queue_name='slow-queue', **kwargs)
