import datetime
import logging

from google.appengine.api import mail

from events import eventdata
import fb_api
from loc import gmaps_api
from loc import math
from logic import friends
from logic import rsvp
import template
from util import dates
from util import fb_mapreduce
from util import text
from util import timings
from util import urls
from . import search

def email_for_user(user, fbl, should_send=True):
    if not user.send_email or not user.email:
        return
    fb_user = fbl.fetched_data(fb_api.LookupUser, fbl.fb_uid)
    if not 'profile' in fb_user:
        return

    user_location = user.location
    if not user_location:
        return
    distance = int(user.distance)
    distance_units = user.distance_units
    if distance_units == 'miles':
        distance_in_km = math.miles_in_km(distance)
    else:
        distance_in_km = distance
    min_attendees = user.min_attendees

    # search for relevant events
    geocode = gmaps_api.get_geocode(address=user_location)
    bounds = math.expand_bounds(geocode.latlng_bounds(), distance_in_km)
    query = search.SearchQuery(time_period=dates.TIME_FUTURE, bounds=bounds, min_attendees=min_attendees)
    fb_user = fbl.fetched_data(fb_api.LookupUser, fbl.fb_uid)

    search_results = query.get_search_results(fbl)
    # Don't send email...
    if not search_results:
        return

    friends.decorate_with_friends(fbl, search_results)
    rsvp.decorate_with_rsvps(fbl, search_results)

    past_results, present_results, grouped_results = search.group_results(search_results)
    # Don't include results more than a month out in these emails
    grouped_results = [x for x in grouped_results if x.id != 'year_events']

    display = {}
    display['date_human_format'] = user.date_human_format
    display['format_html'] = text.format_html
    display['fb_event_url'] = urls.fb_event_url
    display['raw_fb_event_url'] = urls.raw_fb_event_url
    display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
    display['user'] = user
    display['fb_user'] = fb_user

    display['grouped_results'] = grouped_results

    rendered = template.render_template('html_mail_summary', display)
    d = datetime.date.today()
    d = d - datetime.timedelta(days=d.weekday()) # round down to last monday
    logging.info("Rendered HTML:\n%s", rendered)
    message = mail.EmailMessage(
        sender="DanceDeets Events <events@dancedeets.com>",
        subject="Dance events for %s" % d.strftime('%b %d, %Y'),
        to=user.email,
        html=rendered
    )
    if should_send:
        message.send()
    return message

#TODO(lambert): do we really want yield on this one?
@timings.timed
def yield_email_user(fbl, user):
    fbl.request(fb_api.LookupUser, user.fb_uid)
    fbl.request(fb_api.LookupUserEvents, user.fb_uid)
    try:
        fbl.batch_fetch()
    except fb_api.ExpiredOAuthToken as e:
        logging.info("Auth token now expired, mark as such: %s", e)
        user.expired_oauth_token_reason = e.args[0]
        user.expired_oauth_token = True
        user.put()
        return None
    try:
        email = email_for_user(user, fbl, should_send=True)
        return email
    except Exception as e:
        logging.exception("Error sending email for user %s", user.fb_uid)
        return None
map_email_user = fb_mapreduce.mr_user_wrap(yield_email_user)
email_user = fb_mapreduce.nomr_wrap(yield_email_user)

def mr_email_user(fbl):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Email Users',
        #TODO: MOVE
        handler_spec='logic.fb_reloading.map_email_user',
        entity_kind='users.users.User',
    )
