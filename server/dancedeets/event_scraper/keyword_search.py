# -*-*- encoding: utf-8 -*-*-

import datetime
import json
import logging
import time

from dancedeets import base_servlet
from dancedeets import app
from dancedeets import event_types
from dancedeets import fb_api
from dancedeets.util import mr
from dancedeets.util import taskqueue
from dancedeets.util import urls
from . import thing_db
from . import potential_events
from . import event_pipeline
VERTICALS = event_types.VERTICALS


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


obvious_style_keywords = {
    VERTICALS.STREET: ([
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
    ] + two('electro dance') + two('lite feet')),
    VERTICALS.LATIN: [
        'salsa footwork',
    ],
    VERTICALS.CAPOEIRA: [
        'capoeira',
        'capoeira angola',
        'capoeira regional',
        'capoeira contemporânea',
        'capoeira roda',
    ],
    VERTICALS.CONTACT: [
        'kontaktní improvizace',
        'kontaktimprovisation',
        '即興接觸',
        'contacto improvisación',
        'improvisacion de contacto',
        'ci with',
        'ci class',
        'ci jam',
    ]
}

#        'jive',
#        'foxtrot',
#        'waltz',
#        'tango',
#        'quickstep',

too_popular_style_keywords = {
    VERTICALS.STREET: ([
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
    ] + two('hip hop') + two('street dance') + two('new style') + two('all styles')),
    VERTICALS.LATIN: [
        'cha-cha',
        'samba',
        'bachata',
        'rumba',
        'merengue',
        'salsa',
        'afro-cuba',
        'afro-cuban',
        'afrocuban',
        'salsa dance',
        'ladies styling',
        'salsa on1',
        'salsa on2',
        'cuban salsa',
        'salsa cubaine',
        'salsa styling',
        'salsa shine',
        'salsa dance',
        u'サルサ',
        u'サンバ',
        u'バチャータ',
    ],
    VERTICALS.CAPOEIRA: [
        'capoeira',
        'capoeira angola',
        'capoeira regional',
        'capoeira contemporânea',
        'capoeira roda',
    ],
    VERTICALS.SWING: [
        'swing dance',
        'east coast swing',
        'ecs',
        'west coast swing',
        'swing out',
        'wcs',
        'lindy hop',
        'lindy',
        'balboa',
        'solo jazz',
        'solo charleston',
        'partner charleston',
        'carolina shag',
        'collegiate shag',
        'st louis shag',
        'modern jive',
        'jitterbug',
        'slow drag',
    ],
    VERTICALS.ZOUK: [
        'zouk',
        'brazilian zouk',
        'zouk lambada',
    ],
    VERTICALS.BALLROOM: [
        'ballroom dance',
        'latin ballroom',
        'waltz',
        'viennese waltz',
        'tango',
        'foxtrot',
        'quick step',
        'samba',
        'cha cha',
        'rumba',
        'paso doble',
        'jive',
        'east coast swing',
        'bolero',
        'mambo',
        'country 2 step',
        'american tango',
    ],
    VERTICALS.WCS: [
        'west coast swing',
        'wcs',
    ],
    VERTICALS.TANGO: [
        'argentine tango',
        'tango',
        'milonga',
    ],
    VERTICALS.PARTNER_FUSION: [
        'blues fusion',
        'modern jive',
        'ceroc',
        'leroc',
        'le-roc',
        'fusion',
        'fusion dance',
    ],
    VERTICALS.ROCKABILLY: [
        'rockabilly',
        'jive',
        'boogie woogie',
        'rock n roll',
        'rock and roll',
        'rock n roll dance',
        'rock and roll dance',
        'r n r',
        'boogie',
    ],
    VERTICALS.COUNTRY: [
        'country western',
        'country dance',
        'barn dance',
        'square dance',
        'country line',
        'contra barn',
        'cowboy dance',
        'two step',
        'c/w dance',
        'western dance',
        'modern western',
    ],
    VERTICALS: [
        'contact improv',
        'contact improvisaton',
    ]
}

PARTNER = [
    'meeting',
    'incontro',
    'marathon',
    'social',
    'party',
    'jack & jill',
    'weekend',
    'festival',
]

EVERNT_TYPES = [
    'session',
    'workshop',
    'class',
    'taller',
    'stage',
    'lesson',
    'intensive',
    'competition',
    u'competición',
    'competencia',
    'contest',
    'concours',
    'tournaments',
    'performance',
    'spectacle',
    'audition',
    'audiciones',
]
STYLE_EVENT_TYPES = {
    VERTICALS.STREET: [
        'battle',
        'jam',
        'bonnie and clyde',
    ],
    VERTICALS.CAPOEIRA: [
        'roda',
        'encontro',
        'demo',
        'demonstration',
    ],
    VERTICALS.WCS: PARTNER + [],
    VERTICALS.SWING: PARTNER + [
        'hop',
    ],
    VERTICALS.ZOUK: PARTNER + [],
    VERTICALS.PARTNER_FUSION: PARTNER + [],
    VERTICALS.ROCKABILLY: PARTNER + [],
    VERTICALS.COUNTRY: PARTNER + [],
}


def expand_keyword(keyword, style):
    all_keywords = []
    all_keywords.append(keyword)
    for y in EVERNT_TYPES:
        all_keywords.append('%s %s' % (keyword, y))
    for y in STYLE_EVENT_TYPES.get(style, []):
        all_keywords.append('%s %s' % (keyword, y))
    return all_keywords


OBVIOUS = 'OBVIOUS'
TOO_POPULAR = 'TOO_POPULAR'


def get_chunks(style):
    if not style:
        styles = event_types.VERTICALS.__dict__.keys()
    else:
        styles = [style]
    chunks = []
    for style in styles:
        obvious_keywords = obvious_style_keywords.get(style, [])
        too_popular_keywords = too_popular_style_keywords.get(style, [])
        chunks.extend({'type': OBVIOUS, 'keyword': x} for x in obvious_keywords)
        chunks.extend({'type': TOO_POPULAR, 'keyword': x, 'style': style} for x in too_popular_keywords)
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


def get_ids_for_keyword(fbl, query):
    search_results = fbl.get(LookupSearchEvents, query)
    ids = [x['id'] for x in search_results['results']['data']]
    logging.info('Keyword %r returned %s results:', query, len(ids))
    # Debug code
    for x in search_results['results']['data']:
        logging.info('Found %s: %s', x['id'], x.get('name'))

    return ids


def search_fb(fbl, style):
    chunks = get_chunks(style)
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
