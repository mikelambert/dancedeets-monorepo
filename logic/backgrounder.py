from google.appengine.api.labs import taskqueue

def load_events(fb_event_ids, allow_memcache=True):
    fb_uid = '701004' # Mike Lambert
    task_size = 20
    allow_memcache_arg = (allow_memcache and '1' or '0')
    for i in range(0, len(fb_event_ids), task_size):
        taskqueue.add(url='/tasks/load_events', params=dict(user_id=fb_uid, event_ids=','.join(str(x) for x in fb_event_ids[i:i+task_size]), allow_memcache=allow_memcache_arg))
    # Only once we've finished loading the raw events do we bother loading any event members
    for i in range(0, len(fb_event_ids), task_size):
        taskqueue.add(url='/tasks/load_event_members', params=dict(user_id=fb_uid, event_ids=','.join(str(x) for x in fb_event_ids[i:i+task_size]), allow_memcache=allow_memcache_arg))
