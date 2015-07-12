import urllib

def fb_event_url(eid, kwargs=None):
    kwarg_string = '?%s' % urllib.urlencode(kwargs) if kwargs else ''
    return 'http://www.dancedeets.com%s%s' % (fb_relative_event_url(eid), kwarg_string)

def fb_relative_event_url(eid):
    return '/events/%s/' % eid

def raw_fb_event_url(eid):
    return 'http://www.facebook.com/events/%s/' % eid

def dd_admin_event_url(eid):
    return 'http://www.dancedeets.com/events/admin_edit?event_id=%s' % eid

def dd_admin_source_url(eid):
    return 'http://www.dancedeets.com/sources/admin_edit?source_id=%s' % eid

def fb_event_image_url(eid, size='large'):
    return 'https://graph.facebook.com/%s/picture?type=%s' % (eid, size)
