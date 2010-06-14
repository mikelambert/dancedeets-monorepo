import urllib

from google.appengine.api.labs import taskqueue

def load_events(fb_event_ids, allow_cache=True):
    fb_uid = '701004' # Mike Lambert
    task_size = 10
    allow_cache_arg = (allow_cache and '1' or '0')
    #TODO(lambert): use get params instead of post params for transparency
    for i in range(0, len(fb_event_ids), task_size):
        taskqueue.add(url='/tasks/load_events?' + urllib.urlencode(dict(user_id=fb_uid, event_ids=','.join(str(x) for x in fb_event_ids[i:i+task_size]), allow_cache=allow_cache_arg)))
    # Only once we've finished loading the raw events do we bother loading any event members
    for i in range(0, len(fb_event_ids), task_size):
        taskqueue.add(url='/tasks/load_event_members?'+urllib.urlencode(dict(user_id=fb_uid, event_ids=','.join(str(x) for x in fb_event_ids[i:i+task_size]), allow_cache=allow_cache_arg)))
