#!/usr/bin/python
import site
site.addsitedir('lib-local')

from google.cloud import datastore
import json
import logging
import urllib
import urllib2
from dancedeets import keys
from dancedeets.events import web_events_reloading
from dancedeets.events import namespaces
from dancedeets.util import dates

logging.getLogger().setLevel(logging.INFO)


def make_request(server, path, params):
    new_params = params.copy()
    new_params['scrapinghub_key'] = keys.get('scrapinghub_key')
    data = json.dumps(new_params)
    quoted_data = urllib.quote_plus(data)
    f = urllib2.urlopen('http://%s/%s' % (server, path), quoted_data)
    result = f.read()
    return result


def push_items(items):
    path = 'web_events/upload_multi'
    params = {
        'items': items,
    }
    #make_request('dev.dancedeets.com:8080', path, params)
    make_request('www.dancedeets.com', path, params)


def fetch_all_ids(namespace, start_id=1):
    trailing_count = 50
    missing = 0
    id = start_id
    while True:
        item = web_events_reloading.fetch_jwjam(namespace, id)
        logging.info('Downloaded %s:%s: %s', namespace, id, item)
        id += 1

        if item:
            missing = 0
        else:
            missing += 1
        if missing >= trailing_count:
            break

        if not item:
            continue
        push_items([item])
    last_id = id - missing
    return last_id


def find_high_watermark(namespace):
    client = datastore.Client('dancedeets-hrd')
    # Get most recent future event
    query = client.query(kind='DBEvent')
    query.add_filter('namespace_copy', '=', namespace)
    query.order = ['-creation_time']
    #query.keys_only()
    # Get 100 most recent ids, and get the max integer
    results = [x.key for x in query.fetch(100)]
    if results:
        max_id = max([int(x.name.split(':')[1]) for x in results])
        return max_id
    else:
        return 0


def fetch_latest(namespace, start_id=0):
    start_id = find_high_watermark(namespace) or start_id
    fetch_all_ids(namespace, start_id=start_id)


fetch_latest_only = True

if fetch_latest_only:
    fetch_latest(namespaces.CHINA_JWJAM_JAM, 0)
    fetch_latest(namespaces.CHINA_JWJAM_COURSE, 92)
else:
    fetch_all_ids(namespaces.CHINA_JWJAM_JAM, 0)
    fetch_all_ids(namespaces.CHINA_JWJAM_COURSE, 92)
