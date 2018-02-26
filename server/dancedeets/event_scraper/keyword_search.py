# -*-*- encoding: utf-8 -*-*-

import datetime
import json
import logging
import time

from dancedeets import base_servlet
from dancedeets import app
from dancedeets import fb_api
from dancedeets.nlp import styles
from dancedeets.util import mr
from dancedeets.util import taskqueue
from dancedeets.util import urls
from . import thing_db
from . import potential_events
from . import event_pipeline


class LookupSearchEvents(fb_api.LookupType):
    @classmethod
    def track_lookup(cls):
        mr.increment('fb-lookups-search-events')

    @classmethod
    def get_lookups(cls, query):
        return [
            ('results', cls.url('search', type='event', q=query, fields=['id', 'name'], limit=1000)),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fb_api.USERLESS_UID, object_id, 'OBJ_SEARCH')


def expand_keyword(keyword, style_name):
    style = styles.STYLES[style_name]
    all_keywords = ['%s %s' % (keyword, x) for x in style.get_all_keyword_event_types()]
    all_keywords.append(keyword)
    return all_keywords


OBVIOUS = 'OBVIOUS'
TOO_POPULAR = 'TOO_POPULAR'


def get_chunks(style_name):
    if not style_name:
        style_list = styles.STYLES.values()
    else:
        style_list = [styles.STYLES[style_name]]
    chunks = []
    for style in style_list:
        obvious_keywords = style.get_rare_search_keywords()
        too_popular_keywords = style.get_popular_search_keywords()
        chunks.extend({'type': OBVIOUS, 'keyword': x} for x in obvious_keywords)
        chunks.extend({'type': TOO_POPULAR, 'keyword': x, 'style': style.get_name()} for x in too_popular_keywords)
    return chunks


def expand_chunk(chunk):
    if chunk['type'] == OBVIOUS:
        return [chunk['keyword']]
    elif chunk['type'] == TOO_POPULAR:
        return expand_keyword(chunk['keyword'], chunk['style'])
    else:
        raise ValueError('Unknown chunk: %s' % chunk)


def process_ids(fbl, new_ids):
    # This may take awhile...give some breathing room to our FB queries:
    discovered_list = [potential_events.DiscoveredEvent(id, None, thing_db.FIELD_SEARCH) for id in sorted(new_ids)]
    event_pipeline.process_discovered_events(fbl, discovered_list)


def lookup_keywords(fbl, all_keywords):
    logging.info('Looking up %s search queries', len(all_keywords))

    oldest_allowed = fbl.db.oldest_allowed
    # Still want to re-run these queries...but allow re-repeated re-runs to work without hammering FB
    # And we want the searches to expire much more quickly than the servlet as a whole (and event/attending lookups)
    fbl.db.oldest_allowed = datetime.datetime.now() - datetime.timedelta(hours=6)

    all_ids = set()

    for query in all_keywords:
        old_fb_fetches = fbl.fb.fb_fetches
        lookup_time = time.time()
        ids = get_ids_for_keyword(fbl, query)
        new_ids = set(ids).difference(all_ids)
        all_ids.update(ids)

        # Only sleep and space things out, if we actually hit the FB server...
        if old_fb_fetches != fbl.fb.fb_fetches:
            elapsed_time = time.time() - lookup_time
            sleep_time = 2 - elapsed_time
            if sleep_time > 0:
                time.sleep(sleep_time)

        process_ids(fbl, new_ids)

    fbl.db.oldest_allowed = oldest_allowed


def get_id_titles_for_keyword(fbl, query):
    search_results = fbl.get(LookupSearchEvents, query)
    data = search_results['results']['data']
    logging.info('Keyword %r returned %s results:', query, len(data))
    # Debug code
    for x in data:
        logging.info('Found %s: %s', x['id'], x.get('name'))
    return data


def get_ids_for_keyword(fbl, query):
    data = get_id_titles_for_keyword(fbl, query)
    ids = [x['id'] for x in data]
    return ids


def search_fb(fbl, style_name):
    chunks = get_chunks(style_name)
    for chunk in chunks:
        taskqueue.add(
            method='GET',
            url='/tools/search_fb_for_events_for_chunk?' + urls.urlencode(dict(user_id=fbl.fb_uid or 'random', chunk=json.dumps(chunk))),
            queue_name='keyword-search',
        )


@app.route('/tools/search_fb_for_events_for_chunk')
class SearchFbChunkHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        chunk = json.loads(self.request.get('chunk'))
        all_keywords = expand_chunk(chunk)
        lookup_keywords(self.fbl, all_keywords)


@app.route('/tools/search_fb_for_events')
class SearchFbAllHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        style = self.request.get('vertical')
        search_fb(self.fbl, style)
