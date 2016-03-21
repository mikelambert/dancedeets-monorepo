
KOREA_SDK = 'street-dance-korea'
JAPAN_DD = 'dance-delight'
JAPAN_DL = 'dance-life'
JAPAN_DEWS = 'dews'
JAPAN_ETS = 'enter-the-stage'
FACEBOOK = 'FB'


class Namespace(object):
    def __init__(self, short_name, long_name, domain_url, event_url_func):
        self.short_name = short_name
        self.long_name = long_name
        self.domain_url = domain_url
        self.event_url_func = event_url_func

_NAMESPACE_LIST = [
    Namespace(
        FACEBOOK,
        'Facebook',
        'https://www.facebook.com/events/',
        'https://www.facebook.com/%s/',
    ),
    Namespace(
        JAPAN_DD,
        'Dance Delight',
        'http://et-stage.net/event_list.php',
        lambda x: 'http://et-stage.net/event/%s/' % x.namespaced_id,
    ),
    Namespace(
        JAPAN_DL,
        'Dance Life',
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
]

NAMESPACES = dict((x.short_name, x) for x in _NAMESPACE_LIST)
