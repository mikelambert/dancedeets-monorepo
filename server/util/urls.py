import re
import urllib

EVENT_ID_REGEX = r'(?:\d+|[^/?#]+:[^/?#]+)'

def dd_event_url(eid, kwargs=None):
    kwarg_string = '?%s' % urlencode(kwargs) if kwargs else ''
    return 'http://www.dancedeets.com%s%s' % (dd_relative_event_url(eid), kwarg_string)


def dd_relative_event_url(eid):
    return '/events/%s/' % eid


def raw_fb_event_url(eid):
    return 'http://www.facebook.com/events/%s/' % eid


def dd_admin_event_url(eid):
    return 'http://www.dancedeets.com/events/admin_edit?event_id=%s' % eid


def dd_admin_source_url(eid):
    return 'http://www.dancedeets.com/sources/admin_edit?source_id=%s' % eid


def event_image_url(eid, **kwargs):
    encoded_kwargs = urlencode(kwargs)
    url = 'http://www.dancedeets.com/events/image_proxy/%s' % eid
    if encoded_kwargs:
        return '%s?%s' % (url, encoded_kwargs)
    else:
        return url

def urlencode(kwargs, doseq=False):
    if doseq:
        new_kwargs = {}
        for k, v in kwargs.iteritems():
            new_kwargs[unicode(k).encode('utf-8')] = [unicode(v_x).encode('utf-8') for v_x in v]
        kwargs = new_kwargs
    else:
        kwargs = dict((unicode(k).encode('utf-8'), unicode(v).encode('utf-8')) for (k, v) in kwargs.iteritems())
    return urllib.urlencode(kwargs, doseq=doseq)

def get_event_id_from_url(url):
    if '#' in url:
        url = url.split('#')[1]
    match = re.search(r'eid=(\d+)', url)
    if not match:
        match = re.search(r'/events/(%s)(?:/|$)' % EVENT_ID_REGEX, url)
        if not match:
            return None
    return match.group(1)
