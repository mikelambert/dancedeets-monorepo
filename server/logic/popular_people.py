import json
import logging
import random

from google.appengine.ext import ndb
from mapreduce import mapreduce_pipeline
from mapreduce import operation

import app
import base_servlet
import event_types
from events import eventdata
from loc import math
from rankings import cities
import fb_api
from util import fb_mapreduce
from util import runtime

TOP_N = 100

class PeopleRanking(ndb.Model):
    person_type = ndb.StringProperty()
    city = ndb.StringProperty()
    category = ndb.StringProperty()
    top_people = ndb.StringProperty(repeated=True, indexed=False)
    top_people_json = ndb.JsonProperty()
    # top_people_json is [['id: name', count], ...]

    @property
    def human_category(self):
        # '' represents 'Overall'
        return event_types.CATEGORY_LOOKUP.get(self.category, '')

STYLES_SET = set(x.index_name for x in event_types.STYLES)

def get_people_rankings_for_city_names(city_names, attendees_only=False):
    if runtime.is_local_appengine():
        people_rankings = load_from_dev(city_names, attendees_only=attendees_only)
    else:
        args = []
        if attendees_only:
            args = [PeopleRanking.person_type=='ATTENDEE']
        people_rankings = PeopleRanking.query(
            PeopleRanking.city.IN(city_names),
            *args
        )
    return people_rankings

def load_from_dev(city_names, attendees_only):
    from google.cloud import datastore

    rankings = []
    client = datastore.Client()

    for city_name in city_names:
        q = client.query(kind='PeopleRanking')
        q.add_filter('city', '=', city_name)
        if attendees_only:
            q.add_filter('person_type', '=', 'ATTENDEE')

        for result in q.fetch(100):
            ranking = PeopleRanking()
            ranking.person_type = result['person_type']
            ranking.city = result['city']
            ranking.category = result['category']
            #TODO: remove bwcompat code
            ranking.top_people = result.get('top_people')
            ranking.top_people_json = result.get('top_people_json')
            rankings.append(ranking)
    return rankings

def get_city_names_near(latlong):
    if latlong == (None, None):
        return []
    southwest, northeast = math.expand_bounds((latlong, latlong), cities.NEARBY_DISTANCE_KM)
    logging.info('Looking up nearby cities to %s', latlong)
    included_cities = cities.get_nearby_cities((southwest, northeast), only_populated=True)
    logging.info('Found %s cities', len(included_cities))
    biggest_cities = sorted(included_cities, key=lambda x: -x.population)[:10]
    city_names = [city.display_name() for city in biggest_cities]
    return city_names

def get_attendees_near(latlong):
    city_names = get_city_names_near(latlong)
    logging.info('Loading PeopleRanking for top 10 cities: %s', city_names)
    if not city_names:
        return {}
    try:
        people_rankings = get_people_rankings_for_city_names(city_names, attendees_only=True)
        logging.info('Loaded People Rankings')
        groupings = combine_rankings(people_rankings)
    except:
        logging.exception('Error creating combined people rankings')
        return {}
    return groupings.get('ATTENDEE', {})

def combine_rankings(rankings):
    groupings = {}
    for r in rankings:
        #logging.info(r.key)
        key = (r.person_type, r.human_category)
        # Make sure we use setdefault....we can have key repeats due to rankings from different cities
        groupings.setdefault(key, {})
        # Use this version below, and avoid the lookups
        people = groupings[key]
        if r.top_people_json:
            for person_name, count in r.top_people_json:
                if person_name in people:
                    people[person_name] += count
                else:
                    people[person_name] = count
        else:
            #TODO: remove bwcompat code
            for person_triplet in r.top_people:
                person_name, new_count = person_triplet.rsplit(':', 1)
                if person_name in people:
                    people[person_name] += int(new_count)
                else:
                    people[person_name] = int(new_count)
    for key in groupings:
        person_type, category = key
        if person_type == 'ATTENDEE':
            limit = 3
        elif person_type == 'ADMIN':
            limit = 2
        else:
            logging.error('Unknown person type: %s', person_type)
        # Remove low/bad frequency data
        groupings[key] = dict(kv for kv in groupings[key].iteritems() if kv[1] >= limit)

    groupings = dict(kv for kv in groupings.iteritems() if len(kv[1]))

    final_groupings = {}
    for key in groupings:
        person_type, category = key
        orig = groupings[key]
        dicts = []
        for name, count in orig.iteritems():
            split_name = name.split(': ', 1)
            dicts.append({
                'id': split_name[0],
                'name': split_name[1],
                'count': count,
            })
        if person_type not in final_groupings:
            final_groupings[person_type] = {}
        if category not in final_groupings[person_type]:
            final_groupings[person_type][category] = {}
        final_groupings[person_type][category] = sorted(dicts, key=lambda x: -x['count'])
    return final_groupings

@app.route('/tools/popular_people')
class ExportSourcesHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        # TODO: can we somehow trigger the Dataflow job?
        pass
