import datetime
import jinja2
import logging

from google.appengine.api import mail

import fb_api
from loc import gmaps_api
from loc import math
from logic import friends
from logic import rsvp
from users import users
from util import dates
from util import fb_mapreduce
from util import urls
from . import search_base
from . import search

def email_for_user(user, fbl, should_send=True):
    if not user.send_email or not user.email:
        return
    if user.weekly_email_send_date and user.weekly_email_send_date > datetime.datetime.now() - datetime.timedelta(days=3):
        logging.warning("Skipping user %s (%s) because last weekly email was sent on %s", user.fb_uid, user.full_name, user.weekly_email_send_date)
        # Sent the weekly email too recently, let's abort
        return
    fb_user = fbl.fetched_data(fb_api.LookupUser, fbl.fb_uid)
    if not 'profile' in fb_user:
        return

    user_location = user.location
    if not user_location:
        return
    distance_in_km = user.distance_in_km()
    min_attendees = user.min_attendees

    # search for relevant events
    geocode = gmaps_api.get_geocode(address=user_location)
    if not geocode:
        return None
    bounds = math.expand_bounds(geocode.latlng_bounds(), distance_in_km)
    query = search_base.SearchQuery(time_period=dates.TIME_FUTURE, bounds=bounds, min_attendees=min_attendees)
    fb_user = fbl.fetched_data(fb_api.LookupUser, fbl.fb_uid)

    search_results = search.Search(query).get_search_results()
    # Don't send email...
    if not search_results:
        return

    friends.decorate_with_friends(fbl, search_results)
    rsvp.decorate_with_rsvps(fbl, search_results)

    past_results, present_results, grouped_results = search.group_results(search_results, include_all=True)

    display = {}
    display['user'] = user
    display['fb_user'] = fb_user

    week_events = grouped_results[0]
    # Only send emails if we have upcoming events
    if not week_events.results:
        return None
    display['results'] = week_events.results

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    jinja_env.filters['date_human_format'] = user.date_human_format
    jinja_env.globals['fb_event_url'] = urls.fb_event_url
    jinja_env.globals['raw_fb_event_url'] = urls.raw_fb_event_url
    jinja_env.globals['CHOOSE_RSVPS'] = rsvp.CHOOSE_RSVPS
    rendered = jinja_env.get_template('html_mail_summary.html').render(display)
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
        # Update the last-sent-time here, so we any retryable errors don't cause emails to be multi-sent
        user = users.User.get_by_id(user.fb_uid)
        user.weekly_email_send_date = datetime.datetime.now()
        user.put()
        # And send the message now.
        message.send()
    return message

#TODO(lambert): do we really want yield on this one?
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
        handler_spec='search.email_events.map_email_user',
        entity_kind='users.users.User',
    )
