import re
import urllib
from slugify import slugify

EVENT_ID_REGEX = r'(?:\d+|[^/?#]+:[^/?#]+)'


def dd_event_url(eid, kwargs=None):
    kwarg_string = '?%s' % urlencode(kwargs) if kwargs else ''
    return 'https://www.dancedeets.com%s%s' % (dd_relative_event_url(eid), kwarg_string)


def dd_relative_event_url(eid):
    if isinstance(eid, basestring):
        return '/events/%s/' % eid
    else:
        event = eid
        slug = slugify(unicode(event.name))
        return '/events/%s/%s' % (event.id, slug)


def dd_short_event_url(eid):
    return 'http://dd.events/e-%s' % eid


def raw_fb_event_url(eid):
    return 'https://www.facebook.com/events/%s/' % eid


def dd_admin_event_url(eid):
    return 'https://www.dancedeets.com/events/admin_edit?event_id=%s' % eid


def dd_admin_source_url(eid):
    return 'https://www.dancedeets.com/sources/admin_edit?source_id=%s' % eid


def event_image_url(eid, **kwargs):
    encoded_kwargs = urlencode(kwargs)
    url = 'https://d29yoxhmm9n0eh.cloudfront.net/%s' % eid
    if encoded_kwargs:
        return '%s?%s' % (url, encoded_kwargs)
    else:
        return url


def dd_search_url(location, keywords=''):
    return 'https://www.dancedeets.com/?' + urlencode({
        'location': location,
        'keywords': keywords,
    })


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
        match = re.search(r'/events/(%s)(?:[/?]|$)' % EVENT_ID_REGEX, url)
        if not match:
            match = re.search(r'event_id=(%s)(?:[/?]|$)' % EVENT_ID_REGEX, url)
            if not match:
                return None
    return match.group(1)
