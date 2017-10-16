import json
import logging
import urllib
import urllib2
from dancedeets import keys
from dancedeets.events import web_events_reloading
from dancedeets.events import namespaces


def make_request(server, path, params):
    new_params = params.copy()
    new_params['scrapinghub_key'] = keys.get('scrapinghub_key')
    data = json.dumps(new_params)
    quoted_data = urllib.quote_plus(data)
    f = urllib2.urlopen('http://%s/%s' % (server, path), quoted_data)
    result = f.read()
    return result


def push_items(items):
    server = 'dev.dancedeets.com:8080'
    path = 'web_events/upload_multi'
    params = {
        'items': items,
    }
    make_request(server, path, params)


def fetch_all_ids(namespace, start_id=1):
    trailing_count = 20
    missing = 0
    id = start_id
    while True:
        item = web_events_reloading.fetch_jwjam(namespace, id)
        logging.info('Downloaded %s:%s: %s', namespace, id, item)
        id += 1

        if not item:
            continue
        push_items([item])

        if item:
            missing = 0
        else:
            missing += 1
        if missing >= trailing_count:
            break
    last_id = id - missing
    return last_id


def find_high_watermark(namespace):
    # for all events with this namespace
    # sort by namespace id (aka id)
    # and grab the highest-numbered one
    # to return as our watermark
    return 1


def fetch_latest(namespace):
    start_id = find_high_watermark(namespace)
    fetch_all_ids(namespace, start_id=start_id)


fetch_latest_only = True

if fetch_latest_only:
    fetch_latest(namespaces.CHINA_JWJAM_JAM)
    fetch_latest(namespaces.CHINA_JWJAM_COURSE)
else:
    fetch_all_ids(namespaces.CHINA_JWJAM_JAM)
    fetch_all_ids(namespaces.CHINA_JWJAM_COURSE)
