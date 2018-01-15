# -*-*- encoding: utf-8 -*-*-

KOREA_SDK = 'street-dance-korea'
JAPAN_DD = 'dance-delight-1'
JAPAN_DD2 = 'dance-delight-2'
JAPAN_TDL = 'tokyo-dance-life'
JAPAN_DEWS = 'dews'
JAPAN_ETS = 'enter-the-stage'
FACEBOOK = 'FB'
CHINA_JWJAM_JAM = 'jwjam-jam'
CHINA_JWJAM_COURSE = 'jwjam-course'


class Namespace(object):
    def __init__(self, short_name, long_name, domain_url, event_url_func):
        self.short_name = short_name
        self.long_name = long_name
        self.domain_url = domain_url
        self.event_url_func = event_url_func


_NAMESPACE_LIST = [
    Namespace(
        FACEBOOK,
        'Facebook Event',
        'https://www.facebook.com/events/',
        lambda x: 'https://www.facebook.com/%s/' % x.fb_event_id,
    ),
    Namespace(
        JAPAN_DD,
        'Dance Delight',
        'https://www.dancedelight.net/wordpress/?cat=6',
        lambda x: 'https://www.dancedelight.net/wordpress/?p=%s' % x.namespaced_id,
    ),
    Namespace(
        JAPAN_DD2,
        'Dance Delight',
        'http://www.dancedelight.net/event/',
        lambda x: 'http://www.dancedelight.net/event/%s' % x.namespaced_id,
    ),
    Namespace(
        JAPAN_TDL,
        'Tokyo Dance Life',
        'http://www.tokyo-dancelife.com/event/',
        lambda x: 'http://www.tokyo-dancelife.com/event/%s/%s.php' % (x.start_time.strftime('%Y_%m'), x.namespaced_id),
    ),
    Namespace(
        JAPAN_DEWS,
        'DEWS',
        'http://dews365.com/eventinformation',
        lambda x: 'http://dews365.com/event/%s.html' % x.namespaced_id,
    ),
    Namespace(
        JAPAN_ETS,
        'Enter The Stage',
        'http://et-stage.net/event_list.php',
        lambda x: 'http://et-stage.net/event/%s/' % x.namespaced_id,
    ),
    Namespace(
        KOREA_SDK,
        'Street Dance Korea',
        'http://www.streetdancekorea.com',
        # I wish we could link to the event page directly, but alas there is none...
        lambda x: 'http://www.streetdancekorea.com/',
    ),
    Namespace(
        CHINA_JWJAM_JAM,
        u'街舞酱 Jam',
        'http://jwjam.com/Jwjam/Jam/jam_list',
        # I wish we could link to the event page directly, but alas they use obfuscated id URLs
        lambda x: 'http://jwjam.com/Jwjam/Jam/jam_list',
    ),
    Namespace(
        CHINA_JWJAM_COURSE,
        u'街舞酱 Course',
        'http://jwjam.com/Jwjam/Jam/jam_list',
        # I wish we could link to the event page directly, but alas they use obfuscated id URLs
        lambda x: 'http://jwjam.com/Jwjam/Jam/jam_list',
    ),
]

# Ensure our namespaces don't conflict with each other.
# This is especially important when we have to remove the ':' in our taskqueue task names.
for a in _NAMESPACE_LIST:
    for b in _NAMESPACE_LIST:
        if a != b and a.short_name.startswith(b.short_name):
            raise ValueError("Namespaces need different prefixes: %r, %r", a.short_name, b.short_name)

NAMESPACES = dict((x.short_name, x) for x in _NAMESPACE_LIST)
