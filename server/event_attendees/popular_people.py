import hashlib
import json
import logging

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.cloud import datastore

import app
import base_servlet
import event_types
from rankings import cities
from util import runtime

TOP_N = 100

SUMMED_AREA = 'Summed-Area'

class PRDebugAttendee(ndb.Model):
    created_date = ndb.DateTimeProperty(auto_now=True)

    city = ndb.StringProperty()
    person_id = ndb.StringProperty()
    grouped_event_ids = ndb.JsonProperty()

    @staticmethod
    def generate_key(city, category, person_id):
        # TODO: sync with dataflow
        return '%s: %s: %s' % (city, category, person_id)

class PRCityCategory(ndb.Model):
    # key = city + other things
    created_date = ndb.DateTimeProperty(auto_now=True)

    person_type = ndb.StringProperty()
    city = ndb.StringProperty()
    category = ndb.StringProperty()
    top_people_json = ndb.JsonProperty()
    # top_people_json is [['id: name', count], ...]

class PeopleRanking(object):
    def __init__(self, city, category, person_type, top_people_json):
        self.city = city
        self.category = category
        self.person_type = person_type
        self.top_people_json = top_people_json

    def __repr__(self):
        return 'PeopleRanking(%s, %s, %s,\n%s\n)' % (self.city, self.category, self.person_type, self.top_people_json)

    @property
    def human_category(self):
        # '' represents 'Overall'
        return event_types.CATEGORY_LOOKUP.get(self.category, '')

    def worthy_top_people(self, person_index=10, cutoff=0.0):
        results = self._worthy_top_people(person_index, cutoff)
        return [('%s: %s' % (x['person_id'], x['person_name']), x['count']) for x in results]

    def _worthy_top_people(self, person_index, cutoff):
        #return self.top_people_json
        if cutoff > 0:
            cutoff = self.get_worthy_cutoff(person_index, cutoff)
            return [x for x in self.top_people_json if x[1] >= cutoff]
        else:
            return self.top_people_json

    def get_worthy_cutoff(self, person_index, cutoff):
        # If a scene doesn't have "enough people", then the top-person
        # will be drastically different relative to the remainder in the scene.
        # So let's filter people out to ensure they're close to the top-person.
        if self.person_type == 'ATTENDEE':
            minimum = 3
        elif self.person_type == 'ADMIN':
            minimum = 2
        else:
            logging.error('Unknown person type: %s', self.person_type)
        top_person = self.top_people_json[person_index]
        top_person_unique_events = top_person[1]
        return max([int(top_person_unique_events * cutoff), minimum])

def get_people_rankings_for_city_names(city_names, attendees_only=False):
    if runtime.is_local_appengine():
        pr_city_categories = load_from_dev(city_names, attendees_only=attendees_only)
    else:
        args = []
        if attendees_only:
            args = [PRCityCategory.person_type == 'ATTENDEE']
        pr_city_categories = PRCityCategory.query(PRCityCategory.city.IN(city_names), *args).fetch(100)

    results = []
    for city_category in pr_city_categories:
        results.append(PeopleRanking(city_category.city, city_category.category, city_category.person_type, city_category.top_people_json))

    return results

def load_from_dev(city_names, attendees_only):
    rankings = []
    client = datastore.Client()

    for city_name in city_names:
        q = client.query(kind='PRCityCategory')
        q.add_filter('city', '=', city_name)
        if attendees_only:
            q.add_filter('person_type', '=', 'ATTENDEE')

        for result in q.fetch(100):
            ranking = PRCityCategory()
            ranking.key = ndb.Key('PRCityCategory', result.key.name)
            ranking.person_type = result['person_type']
            ranking.city = result['city']
            ranking.category = result['category']
            ranking.top_people_json = json.loads(result.get('top_people_json', '[]'))
            rankings.append(ranking)
    return rankings

def _get_city_names_within(bounds):
    if bounds == None:
        return []
    logging.info('Looking up nearby cities to %s', bounds)
    included_cities = cities.get_nearby_cities(bounds, only_populated=True)
    logging.info('Found %s cities', len(included_cities))
    biggest_cities = sorted(included_cities, key=lambda x: -x.population)[:10]
    city_names = [city.display_name() for city in biggest_cities]
    return city_names

def get_attendees_within(bounds, max_attendees):
    city_names = _get_city_names_within(bounds)
    logging.info('Loading PRCityCategory for top 10 cities: %s', city_names)
    if not city_names:
        return {}
    memcache_key = 'AttendeeOnly: %s' % hashlib.md5('\n'.join(city_names).encode('utf-8')).hexdigest()
    memcache_result = memcache.get(memcache_key)
    if memcache_result:
        logging.info('Reading memcache key %s with value length: %s', memcache_key, len(memcache_result))
        result = json.loads(memcache_result)
    else:
        people_rankings = get_people_rankings_for_city_names(city_names, attendees_only=True)
        logging.info('Loaded %s People Rankings', len(people_rankings))
        if runtime.is_local_appengine() and False:
            for x in people_rankings:
                logging.info(x.key)
                for person in x.worthy_top_people():
                    logging.info('  - %s' % person)
        groupings = combine_rankings(people_rankings, max_people=max_attendees)
        result = groupings.get('ATTENDEE', {})
        # Trim out the unnecessary names
        for category_city, people in result.iteritems():
            for person in people:
                del person['name']
        json_dump = json.dumps(result)
        try:
            logging.info('Writing memcache key %s with value length: %s', memcache_key, len(json_dump))
            memcache.set(memcache_key, json_dump, time=24 * 60 * 60)
        except ValueError:
            logging.warning('Error writing memcache key %s with value length: %s', memcache_key, len(json_dump))
            logging.warning('Tried to write: %s', json.dumps(result, indent=2))
    return result

def combine_rankings(rankings, max_people=0):
    groupings = {}
    for r in rankings:
        top_people = r.worthy_top_people()
        if not top_people:
            continue
        #logging.info(r.key)
        for key in (
            (SUMMED_AREA, r.person_type, r.category),
            (r.city, r.person_type, r.category),
        ):
            # Make sure we use setdefault....we can have key repeats due to rankings from different cities
            groupings.setdefault(key, {})
            # Use this version below, and avoid the lookups
            people = groupings[key]
            people_list = top_people[:max_people] if max_people else top_people
            for person_name, count in people_list[:TOP_N]:
                if person_name in people:
                    people[person_name] += count
                else:
                    people[person_name] = count
    for key in groupings:
        city, person_type, category = key
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
        city, person_type, category = key
        secondary_key = '%s: %s' % (category, city)
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
        if secondary_key not in final_groupings[person_type]:
            final_groupings[person_type][secondary_key] = {}
        # Sort by count, then by name (for stable sorting)
        final_groupings[person_type][secondary_key] = sorted(dicts, key=lambda x: (-x['count'], x['id']))
    return final_groupings

@app.route('/tools/popular_people')
class ExportSourcesHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        # TODO: can we somehow trigger the Dataflow job?
        pass
