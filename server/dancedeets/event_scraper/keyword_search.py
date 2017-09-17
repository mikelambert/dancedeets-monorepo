# -*-*- encoding: utf-8 -*-*-

import datetime
import time

from dancedeets import base_servlet
from dancedeets import app
import logging
from dancedeets import fb_api
from dancedeets.util import mr
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


def two(w):
    a, b = w.split(' ')
    keywords = [
        '%s %s' % (a, b),
        '%s%s' % (a, b),
    ]
    return keywords


def search_fb(fbl):
    obvious_keywords = ([
        'bboys',
        'bboying',
        'bgirl',
        'bgirls',
        'bgirling',
        'breakdancing',
        'breakdancers',
        'breakdanse',
        'hiphop',
        'hip hop',
        'new style',
        'house danse',
        'afro house',
        'afrohouse',
        'poppers',
        'poplock',
        'tutting',
        'bopping',
        'boppers',
        'lockers',
        'locking',
        'waacking',
        'waackers',
        'waack',
        'whacking',
        'whackers',
        'jazzrock',
        'jazz rock',
        'jazz-rock',
        'ragga jam',
        'krump',
        'krumperz',
        'krumping',
        'streetjazz',
        'voguing',
        'house danse',
        'hiphop dance',
        'hiphop danse',
        'hip hop danse',
        'tous style',
        'urban dance',
        'afro house',
        'urban style',
        'turfing',
        'baile urbano',
        'soul dance',
        'footwork',
        '7 to smoke',
        u'ストリートダンス',
        u'ブレックダンス',
        'cypher',
        'cypher battle',
        'cypher jam',
    ] + two('electro dance') + two('lite feet'))
    too_popular_keywords = ([
        'bboy',
        'breaking',
        'breakdance',
        'house dance',
        'bebop',
        'dancehall',
        'street jazz',
        'street-jazz',
        'hip hop dance',
        # 'house workshop'....finds auto-add events we don't want labelled as house or as dance events
        # so we don't want to list it here..
        #'waving',
        #'boogaloo',
        # 'uk jazz', 'uk jazz', 'jazz fusion',
        # 'flexing',
        'lock',
        'popping',
        'dance',
        'choreo',
        'choreography',
        #'kpop', 'k pop',
        'vogue',
        'all styles',
        'freestyle',
    ] + two('hip hop') + two('street dance') + two('new style') + two('all styles'))
    event_types = [
        'session',
        'workshop',
        'class',
        'taller',
        'stage',
        'lesson',
        'battle',
        'jam',
        'competition',
        'competición',
        'competencia',
        'contest',
        'concours',
        'tournaments',
        'performance',
        'spectacle',
        'audition',
        'audiciones',
        'bonnie and clyde',
    ]
    all_keywords = obvious_keywords[:]
    for x in too_popular_keywords:
        all_keywords.append(x)
        for y in event_types:
            all_keywords.append('%s %s' % (x, y))

    logging.info('Looking up %s search queries', len(all_keywords))

    all_ids = set()
    oldest_allowed = fbl.db.oldest_allowed
    # Still want to re-run these queries...but allow re-repeated re-runs to work without hammering FB
    # And we want the searches to expire much more quickly than the servlet as a whole (and event/attending lookups)
    fbl.db.oldest_allowed = datetime.datetime.now() - datetime.timedelta(hours=6)

    for query in all_keywords:
        old_fb_fetches = fbl.fb.fb_fetches
        search_results = fbl.get(LookupSearchEvents, query)
        ids = [x['id'] for x in search_results['results']['data']]
        all_ids.update(ids)
        logging.info('Keyword %r returned %s results:', query, len(ids))
        # Debug code
        for x in search_results['results']['data']:
            logging.info('Found %s: %s', x['id'], x.get('name'))

        # Only sleep and space things out, if we actually hit the FB server...
        if old_fb_fetches != fbl.fb.fb_fetches:
            time.sleep(2)

    fbl.db.oldest_allowed = oldest_allowed

    # Run these all_ids in a queue of some sort...to process later, in groups?
    discovered_list = [potential_events.DiscoveredEvent(id, None, thing_db.FIELD_SEARCH) for id in sorted(all_ids)]

    event_pipeline.process_discovered_events(fbl, discovered_list)


@app.route('/tools/search_fb_for_events')
class ByBaseHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        search_fb(self.fbl)
