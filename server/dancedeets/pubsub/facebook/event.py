# -*-*- encoding: utf-8 -*-*-

import json
import logging
import random

from dancedeets import fb_api
from dancedeets import fb_api_util
from dancedeets.users import users
from dancedeets.util import text
from .. import common
from .. import db


class LookupGeoTarget(fb_api.LookupType):
    @classmethod
    def get_lookups(cls, urlparams):
        return [
            ('search', cls.url('search', type='adgeolocation', **urlparams)),
        ]

    @classmethod
    def cache_key(cls, query, fetching_uid):
        return (fb_api.USERLESS_UID, json.dumps(query, sort_keys=True), 'OBJ_GEO_TARGET')


def facebook_post(auth_token, db_event):
    link = common.campaign_url(db_event, 'fb_feed')
    datetime_string = db_event.start_time.strftime('%s @ %s' % (common.DATE_FORMAT, common.TIME_FORMAT))

    page_id = auth_token.token_nickname
    endpoint = 'v2.9/%s/feed' % page_id
    fbl = fb_api.FBLookup(None, auth_token.oauth_token)

    post_values = {}
    # post_values['message'] = db_event.name
    post_values['link'] = link
    post_values['name'] = db_event.name
    post_values['caption'] = datetime_string
    name = _get_posting_user(db_event)

    human_date = db_event.start_time.strftime('%B %-d')
    # TODO: Sometimes we definitely know the City (from a lat/long), but FB doesn't give us a city.
    # Hopefully in the Great Event Location Cleanup, can take care of this...
    if db_event.city:
        location = db_event.city
    else:
        location = ''

    host = ''
    admins = db_event.admins
    if admins:
        admin_ids = [x['id'] for x in admins]
        page_admin_ids = fb_api_util.filter_by_type(fbl, admin_ids, 'page')
        # TODO: Can I @mention the people here too, like I do as a human? Or does it only work with pages?
        host = text.human_list('@[%s]' % x for x in page_admin_ids)

    # Tag it if we can
    if db_event.venue_id:
        venue = '@[%s]' % db_event.venue_id
    else:
        venue = db_event.location_name

    if not location:
        # Don't want to post events globally...too noisy
        return {}

    params = {
        'location': location,
        'date': human_date,
        'venue': venue,
    }
    messages = [
        'Dancers, are you ready? %(venue)s has an event on %(date)s in %(location)s.',
        'Hello %(location)s dancers, mark your calendars! We just found a new dance event on %(date)s at %(venue)s.',
        'Hey %(location)s dancers, save the date! Look what we found coming up on %(date)s at %(venue)s.',
        'Just posted! We have an upcoming dance event on %(date)s at %(venue)s in %(location)s.',
        'What\'s up %(location)s, there\'s a dance event at %(venue)s on %(date)s.',
    ]
    message = random.choice(messages) % params
    if host and host != venue:
        message += random.choice([
            ' Hosted by our friends at %(host)s.',
            ' Thanks to our buddies at %(host)s for hosting!',
            ' Hitup the awesome %(host)s with any questions you\'ve got!',
        ]) % {
            'host': host
        }
    if name:
        message += random.choice([
            ' Thanks to %(name)s for adding it to DanceDeets!',
            ' And a special thanks to %(name)s, for sharing it with you all on DanceDeets!',
            ' This event brought to you on DanceDeets courtesy of %(name)s!',
        ]) % {
            'name': name
        }
    post_values['message'] = message

    description = db_event.description
    if len(description) > 10000:
        post_values['description'] = description[:9999] + u"…"
    else:
        post_values['description'] = description
    post_values['description'] = post_values['description']
    cover = db_event.largest_cover
    if cover:
        post_values['picture'] = cover['source']
    venue_id = db_event.venue_id
    if venue_id:
        post_values['place'] = venue_id

    feed_targeting = get_country_targeting_data(fbl, db_event)
    if feed_targeting:
        # Ideally we'd do this as 'feed_targeting', but Facebook appears to return errors with that due to:
        # {u'error': {u'message': u'Invalid parameter', u'code': 100, u'is_transient': False,
        #  u'error_user_title': u'Invalid Connection', u'error_subcode': 1487124, u'type': u'FacebookApiException',
        #  u'error_user_msg': u'You can only specify connections to objects you are an administrator or developer of.',
        #  u'error_data': {u'blame_field': u'targeting'}}}
        post_values['targeting'] = json.dumps(feed_targeting)

    logging.info("FB Feed Post Values: %s", post_values)
    return fbl.fb.post(endpoint, None, post_values)


def get_country_targeting_data(fbl, db_event):
    short_country = db_event.country
    feed_targeting = {
        'countries': [short_country],
    }
    full_targeting = {'geo_locations': feed_targeting}
    return full_targeting


def get_targeting_data(fbl, db_event):
    city_key = None

    short_country = db_event.country
    if short_country:
        city_state_list = [
            db_event.city,
            db_event.state,
        ]
        city_state = ', '.join(x for x in city_state_list if x)
        geo_search = {
            'location_types': 'city,region',
            'country_code': db_event.country,
            'q': city_state,
        }
        geo_target = fbl.get(LookupGeoTarget, geo_search, allow_cache=False)

        good_targets = geo_target['search']['data']
        if good_targets:
            # Is usually an integer, but in the case of HK and SG (city/country combos), it can be a string
            city_key = good_targets[0]['key']
            # if we want state-level targeting, 'region_id' would be the city's associated state

    if not short_country:
        geocode = db_event.get_geocode()
        if geocode:
            short_country = geocode.country()

    feed_targeting = {}
    # Target by city if we can, otherwise use the country
    if city_key:
        feed_targeting['cities'] = [{
            'key': city_key,
            #'radius': 80,
            #'distance_unit': 'kilometer',
        }]
    elif short_country:
        feed_targeting['countries'] = [short_country]
    full_targeting = {'geo_locations': feed_targeting}
    return full_targeting


def _get_posting_user(db_event):
    # STR_ID_MIGRATE
    if db_event.creating_fb_uid and db_event.creating_fb_uid != 701004:
        user = users.User.get_by_id(str(db_event.creating_fb_uid))
        name = user.full_name
        return name
    else:
        return None


def get_dancedeets_fbl():
    page_id = '110312662362915'
    #page_id = '1375421172766829' # DD-Manager-Test
    tokens = db.OAuthToken.query(
        db.OAuthToken.user_id == '701004', db.OAuthToken.token_nickname == page_id, db.OAuthToken.application == db.APP_FACEBOOK
    ).fetch(1)
    if tokens:
        return fb_api.FBLookup(None, tokens[0].oauth_token)
    else:
        return None


def post_on_event_wall(db_event):
    logging.info("Considering posting on event wall for %s", db_event.id)
    fbl = get_dancedeets_fbl()
    if not fbl:
        logging.error("Failed to find DanceDeets page access token.")
        return

    url = common.campaign_url(db_event, 'fb_event_wall')
    name = _get_posting_user(db_event) or "we've"
    messages = [
        (
            'Congrats, %(name)s added this dance event to DanceDeets, the site for street dance events worldwide! '
            'Dancers can discover this event in our DanceDeets mobile app, or on our website here: %(url)s'
        ),
        (
            'Yay, %(name)s included your event on our DanceDeets website and mobile app for interested dancers. '
            'You can check it out here, and good luck with your event! %(url)s'
        ),
        (
            'Hey there, %(name)s listed this event on DanceDeets, the website/mobile-app for street dancers worldwide. '
            "We're sure you'll have a great event, but we hope our site can help with that in a small way... %(url)s"
        ),
        (
            'Awesome, %(name)s added your dance event to DanceDeets, to help more dancers discover it. '
            "Hopefully you don't mind the extra help in promoting your event! %(url)s"
        ),
    ]
    message = random.choice(messages) % {'name': name, 'url': url}
    logging.info("Attempting to post on event wall for %s", db_event.id)
    result = fbl.fb.post('v2.9/%s/feed' % db_event.fb_event_id, None, {
        'message': message,
        'link': url,
    })
    return result
