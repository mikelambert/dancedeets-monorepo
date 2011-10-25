import urllib

from google.appengine.api import taskqueue

def load_event_attending(fb_event_ids, allow_cache=True, **kwargs):
    fb_uid = '701004' # Mike Lambert
    task_size = 10
    allow_cache_arg = (allow_cache and '1' or '0')
    for i in range(0, len(fb_event_ids), task_size):
        taskqueue.add(method='GET', url='/tasks/load_event_attending?'+urllib.urlencode(dict(user_id=fb_uid, event_ids=','.join(str(x) for x in fb_event_ids[i:i+task_size]), allow_cache=allow_cache_arg)), queue_name='slow-queue', **kwargs)

def load_potential_events_for_friends(user_id, fb_uids, allow_cache=True, **kwargs):
    task_size = 10
    allow_cache_arg = (allow_cache and '1' or '0')
    for i in range(0, len(fb_uids), task_size):
        taskqueue.add(method='GET', url='/tasks/load_potential_events_for_user?' + urllib.urlencode(dict(user_id=user_id, user_ids=','.join(str(x) for x in fb_uids[i:i+task_size]), allow_cache=allow_cache_arg)), queue_name='slow-queue', **kwargs)

def update_last_login_time(user_id):
    taskqueue.add(method='GET', url='/tasks/update_last_login_time?user_id=%s' % user_id, queue_name='slow-queue')
