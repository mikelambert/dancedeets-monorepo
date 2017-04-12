# -*-*- encoding: utf-8 -*-*-

import datetime
import json
import logging
import random

import fb_api
from loc import math
from rankings import cities
from search import search_base
from search import search
from util import urls
from .facebook import event

def _generate_post_for(city, search_results):
    post_values = {}
    headers = [
        "Hey %(location)s, here's what's coming up for you this week in dance!",
        "Here's your dance schedule for this week in %(location)s:",
        "Your street dance calendar this week for %(location)s:",
        "Wondering where to dance this week in %(location)s? Here's what's coming up!",
    ]
    footers = [
        'Did we miss anything? Chime in and let us know!',
        'Want us to grab your event for next week? Make sure you click Add Event on dancedeets.com!',
        'Did we forget your event? Let us know!',
    ]

    messages = []
    messages.append(random.choice(headers) % {'location': city.city_name})

    for result in search_results:
        dt = result.start_time.strftime('%a %-H:%M')
        event = result.db_event
        if event.venue_id:
            location = ' @ @[%s]' % event.venue_id
        elif event.location_name:
            location = ' @ %s' % event.location_name
        else:
            location = ''
        params = {
            'daytime': dt,
            'name': result.name,
            'location': location,
            'url': urls.dd_event_url(result.event_id),
        }
        line = '%(daytime)s: %(name)s%(location)s: %(url)s' % params
        messages.append(line)
        messages.append('')

    messages.append(random.choice(footers))

    post_values['message'] = '\n'.join(messages)

    #TODO: attach a bunch of event flyers to this post!

    logging.info("FB Feed Post Values: %s", post_values)
    return post_values


def _generate_results_for(city):
    d = datetime.date.today()
    monday = d - datetime.timedelta(days=d.weekday()) # round down to last monday
    start_time = monday
    end_time = start_time + datetime.timedelta(days=8)

    latlng_bounds = ((city.latitude, city.longitude), (city.latitude, city.longitude))
    city_bounds = math.expand_bounds(latlng_bounds, cities.NEARBY_DISTANCE_KM)
    search_query = search_base.SearchQuery(
        time_period=search_base.TIME_ALL_FUTURE,
        start_date=start_time,
        end_date=end_time,
        bounds=city_bounds
    )
    searcher = search.Search(search_query)
    search_results = searcher.get_search_results(full_event=True)
    return search_results

def facebook_weekly_post(db_auth_token, city_data):
    city_key = city_data['city']
    city = cities.City.get_by_key_name(city_key)
    page_id = db_auth_token.token_nickname
    endpoint = 'v2.8/%s/feed' % page_id
    fbl = fb_api.FBLookup(None, db_auth_token.oauth_token)

    search_results = _generate_results_for(city)
    if len(search_results) < 2:
        return False
    post_values = _generate_post_for(city, search_results)

    feed_targeting = get_city_targeting_data(fbl, city)
    if feed_targeting:
        # Ideally we'd do this as 'feed_targeting', but Facebook appears to return errors with that due to:
        # {u'error': {u'message': u'Invalid parameter', u'code': 100, u'is_transient': False,
        #  u'error_user_title': u'Invalid Connection', u'error_subcode': 1487124, u'type': u'FacebookApiException',
        #  u'error_user_msg': u'You can only specify connections to objects you are an administrator or developer of.',
        #  u'error_data': {u'blame_field': u'targeting'}}}
        post_values['targeting'] = json.dumps(feed_targeting)
    result = fbl.fb.post(endpoint, None, post_values)
    logging.info('Post Result for %s: %s', city.display_name(), result)
    return result


def get_city_targeting_data(fbl, city):
    city_key = None

    city_state_list = [
        city.city_name,
        city.state_name,
    ]
    city_state = ', '.join(x for x in city_state_list if x)
    geo_search = {
        'location_types': 'city',
        'country_code': city.country_name,
        'q': city_state,
    }
    geo_target = fbl.get(event.LookupGeoTarget, geo_search)

    good_targets = geo_target['search']['data']
    if good_targets:
        # Is usually an integer, but in the case of HK and SG (city/country combos), it can be a string
        city_key = good_targets[0]['key']
        # if we want state-level targeting, 'region_id' would be the city's associated state

    feed_targeting = {}
    # Target by city if we can, otherwise use the country
    if city_key:
        feed_targeting['cities'] = [{
            'key': city_key,
            'radius': 80,
            'distance_unit': 'kilometer',
        }]
    full_targeting = {'geo_locations': feed_targeting}
    return full_targeting
