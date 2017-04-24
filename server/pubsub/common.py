from util import urls

DATE_FORMAT = "%Y/%m/%d"
TIME_FORMAT = "%H:%M"

def campaign_url(eid, source):
    return urls.dd_event_url(eid, {
        'utm_source': source,
        'utm_medium': 'share',
        'utm_campaign': 'autopost'
    })
