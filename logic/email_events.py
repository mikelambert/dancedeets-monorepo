import datetime
import logging

from google.appengine.api import mail

from events import eventdata
from events import tags
from events import users
import fb_api
import locations
from logic import potential_events
from logic import rsvp
from logic import search
import template
from util import text

def email_for_user(user, batch_lookup, fb_graph):
    if not user.send_email:
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
    freestyle = user.freestyle
    choreo = user.choreo

    # search for relevant events
    latlng_user_location = locations.get_geocoded_location(user_location)['latlng']
    query = search.SearchQuery(time_period=tags.TIME_FUTURE, location=latlng_user_location, distance_in_km=distance_in_km, freestyle=freestyle, choreo=choreo)
    search_results = query.get_search_results(user.fb_uid, fb_graph)
    # Don't send email...
    if not search_results:
        return
    rsvp.decorate_with_rsvps(batch_lookup, search_results)
    past_results, present_results, grouped_results = search.group_results(search_results)
    # Don't include results more than a month out in these emails
    grouped_results = [x for x in grouped_results if x.id != 'year_events']

    # check the events user-was-invited-to, looking for any dance-related fb events we don't know about yet
    new_dance_events = potential_events.get_potential_dance_events(batch_lookup, user)

    display = {}
    display['date_human_format'] = users.date_human_format
    display['format_html'] = text.format_html
    display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
    display['user'] = user
    display['fb_user'] = batch_lookup.data_for_user(user.fb_uid)

    display['new_dance_events'] = new_dance_events

    display['grouped_results'] = grouped_results

    rendered = template.render_template('html_mail_summary', display)
    d = datetime.date.today()
    d = d - datetime.timedelta(days=d.weekday()) # round down to last monday
    logging.info("Rendered HTML:\n%s", rendered)
    message = mail.EmailMessage(
        sender="DanceDeets Events <events@dancedeets.com>",
        subject="Dance events for %s" % d.strftime('%b %d, %Y'),
        to=batch_lookup.data_for_user(user.fb_uid)['profile']['email'],
        html=rendered
    )
    message.send()

