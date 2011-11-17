import datetime
import logging

from google.appengine.api import mail

from events import eventdata
from events import users
import fb_api
import locations
from logic import potential_events
from logic import friends
from logic import rsvp
from logic import search
import template
from util import text
from util import urls

def email_for_user(user, batch_lookup, fb_graph, should_send=True):
    if not user.send_email or not user.email:
        return
    fb_user = batch_lookup.data_for_user(batch_lookup.fb_uid)
    if not 'profile' in fb_user:
        return

    user_location = user.location
    if not user_location:
        return
    distance = int(user.distance)
    distance_units = user.distance_units
    if distance_units == 'miles':
        distance_in_km = locations.miles_in_km(distance)
    else:
        distance_in_km = distance
    min_attendees = user.min_attendees

    # search for relevant events
    latlng_user_location = locations.get_geocoded_location(user_location)['latlng']
    query = search.SearchQuery(time_period=eventdata.TIME_FUTURE, location=latlng_user_location, distance_in_km=distance_in_km, min_attendees=min_attendees)
    search_results = query.get_search_results(user.fb_uid, fb_graph)
    # Don't send email...
    if not search_results:
        return

    friends.decorate_with_friends(batch_lookup, search_results)
    rsvp.decorate_with_rsvps(batch_lookup, search_results)

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
