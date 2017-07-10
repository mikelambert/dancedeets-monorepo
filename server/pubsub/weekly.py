# -*-*- encoding: utf-8 -*-*-

import datetime
import json
import logging
import random

import fb_api
from loc import math
from rankings import cities
from rankings import cities_db
from search import search_base
from search import search
from util import urls
from .facebook import event
from .facebook import fb_util
from . import weekly_images

def _generate_post_for(city, week_start, search_results):
    headers = [
        "Hey %(location)s, here's what's coming up for you this week in dance!",
        "Here's your dance schedule for this week near %(location)s:",
        "Your street dance calendar this week for %(location)s:",
        "Wondering where to dance this week near %(location)s? Here's what's coming up!",
    ]
    footers = [
        'Did we miss anything? Chime in and let us know!',
        'Want us to grab your event for next week? Make sure you click Add Event on dancedeets.com!',
        'Did we forget your event? Let us know!',
    ]

    messages = []
    messages.append(random.choice(headers) % {'location': city.city_name})
    #TODO: add link to the week's events
    last_result = None
    for result in search_results:
        if not last_result or last_result.start_time.strftime('%A') != result.start_time.strftime('%A'):
            messages.append('')
            messages.append(result.start_time.strftime('%A %B %-d:'))
        # AM/PM countries
        if city.country_name in ['US', 'UK', 'PH', 'CA', 'AU', 'NZ', 'IN', 'EG', 'SA', 'CO', 'PK', 'MY']:
            dt = result.start_time.strftime('%-I:%M%p')
        else:
            dt = result.start_time.strftime('%-H:%M')
        if result.db_event.venue_id:
            location = ' @ @[%s]' % result.db_event.venue_id
        #elif result.db_event.location_name:
        #    location = ' @ %s' % result.db_event.location_name
        else:
            location = ''
        params = {
            'daytime': dt,
            'name': result.name,
            'location': location,
            'url': urls.dd_short_event_url(result.event_id),
        }
        messages.append('- %(daytime)s: %(name)s%(location)s:' % params)
        messages.append('  %(url)s' % params)
        messages.append('')
        last_result = result

    messages.append(random.choice(footers))

    return '\n'.join(messages)


def _generate_results_for(city, week_start):
    start_time = week_start
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
    result = _facebook_weekly_post(db_auth_token, city_data)
    return fb_util.processed_task(db_auth_token, result)

def _facebook_weekly_post(db_auth_token, city_data):
    city_key = city_data['city']

    city = cities.City.get_by_key_name(city_key)
    page_id = db_auth_token.token_nickname
    fbl = fb_api.FBLookup(None, db_auth_token.oauth_token)

    d = datetime.date.today()
    week_start = d - datetime.timedelta(days=d.weekday()) # round down to last monday

    search_results = _generate_results_for(city, week_start)
    if len(search_results) < 2:
        return {}

    # Generate image on GCS
    image_url = weekly_images.build_and_cache_image(city, week_start, search_results)

    # Generate the weekly text post
    message = _generate_post_for(city, week_start, search_results)

    # Can't upload image to FB Page...as the uploaded photo then becomes un-animated
    # So instead lets link to the image from our FB post

    # Now post to FB Feed about it
    post_values = {
        'message': message,
        'link': image_url,
    }
    feed_targeting = get_city_targeting_data(fbl, city)
    if feed_targeting:
        # Ideally we'd do this as 'feed_targeting', but Facebook appears to return errors with that due to:
        # {u'error': {u'message': u'Invalid parameter', u'code': 100, u'is_transient': False,
        #  u'error_user_title': u'Invalid Connection', u'error_subcode': 1487124, u'type': u'FacebookApiException',
        #  u'error_user_msg': u'You can only specify connections to objects you are an administrator or developer of.',
        #  u'error_data': {u'blame_field': u'targeting'}}}
        post_values['targeting'] = json.dumps(feed_targeting)
    logging.info("FB Feed Post Values: %s", post_values)
    endpoint = 'v2.9/%s/feed' % page_id
    result = fbl.fb.post(endpoint, None, post_values)
    logging.info('Post Result for %s: %s', city.display_name(), result)
    return result


def get_city_targeting_data(fbl, city):
    nearby_cities = cities_db.get_nearby_cities((city.latitude, city.longitude), distance=cities_db.NEARBY_DISTANCE_KM)
    key_types = set((x.adgeolocation_key, x.adgeolocation_type) for x in nearby_cities)

    city_keys = [x[0] for x in key_types if x[1] == 'city'][:250]
    region_keys = [x[0] for x in key_types if x[1] == 'region'][:200]

    feed_targeting = {}
    if city_keys:
        feed_targeting['cities'] = [{
            'key': city_key,
        } for city_key in city_keys]
    if region_keys:
        feed_targeting['regions'] = [{
            'key': region_key,
        } for region_key in region_keys]
    full_targeting = {'geo_locations': feed_targeting}
    return full_targeting
