# -*-*- encoding: utf-8 -*-*-


import base_servlet
import app
import fb_api
from util import mr
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
            ('results', cls.url('search', type='event', q=query, fields=['id'], limit=1000)),
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
        'bboy', 'bboys', 'bboying', 'bgirl', 'bgirls', 'bgirling', 'breakdance', 'breakdancing', 'breakdancers',
        'hiphop', 'hip hop', 'hip-hop', 'new style',
        'house dance', 'house danse',
        'poppers', 'poplock',
        'tutting', 'bopping', 'boppers',
        'lockers', 'locking',
        'waacking', 'waackers', 'waack', 'whacking', 'whackers',
        'bebop', 'jazzrock', 'jazz rock', 'jazz-rock',
        'dancehall', 'ragga jam',
        'krump', 'krumperz', 'krumping',
        'street jazz', 'street-jazz', 'streetjazz',
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
    ] + two('street dance')
      + two('electro dance')
      + two('lite feet')
    )
    too_popular_keywords = ([
        'breaking',
        # TODO: 'house workshop'....finds auto-add events we don't want labelled as house or as dance events
        'house',
        #'waving',
        #'boogaloo',
        # 'uk jazz', 'uk jazz', 'jazz fusion',
        # 'flexing',
        'lock',
        'popping',
        'dance', 'choreo', 'choreography',
        'kpop', 'k pop',
        'vogue',
        'bonnie and clyde',
    ] + two('hip hop')
      + two('new style')
      + two('all style')
      + two('all styles')
      + two('free style')
    )
    event_types = [
        'session',

        'workshop',
        'class', 'taller', 'stage',

        'battle',
        'jam',
        'competition', 'competición', 'competencia',
        'contest', 'concours',
        'tournaments',

        'performance', 'spectacle',

        'party', 'parties',
        'audition', 'audiciones',
    ]
    all_keywords = obvious_keywords[:]
    for x in too_popular_keywords:
        for y in event_types:
            all_keywords.append('%s %s' % (x, y))

    all_ids = set()
    for query in all_keywords[:1]:
        search_results = fbl.get(LookupSearchEvents, query)
        ids = [x['id'] for x in search_results['results']['data']]
        all_ids.update(ids)

    print all_ids

    # Run these all_ids in a queue of some sort...to process later, in groups?
    discovered_list = [potential_events.DiscoveredEvent(id, None, thing_db.FIELD_SEARCH) for id in sorted(all_ids)]

    event_pipeline.process_discovered_events(fbl, discovered_list[6:8])



@app.route('/tools/search_fb_for_events')
class ByBaseHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        search_fb(self.fbl)
