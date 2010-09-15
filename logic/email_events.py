import logging

from google.appengine.api import mail

from events import eventdata
from events import tags
import locations
from logic import rsvp
from logic import search
import template
from util import text

def email_for_user(user, batch_lookup, fb_graph, parse_fb_timestamp):
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

    latlng_user_location = locations.get_geocoded_location(user_location)['latlng']
    query = search.SearchQuery(parse_fb_timestamp, time_period=tags.TIME_FUTURE, location=latlng_user_location, distance_in_km=distance_in_km, freestyle=freestyle, choreo=choreo)
    search_results = query.get_search_results(user.fb_uid, fb_graph)
    rsvp.decorate_with_rsvps(batch_lookup, search_results)
    
    display = {}
    display['date_human_format'] = user.date_human_format
    display['format_html'] = text.format_html
    display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS

    display['results'] = search_results
    rendered = template.render_template('html_mail_summary', display)
    d = datetime.date.today()
    d = d - datetime.timedelta(days=d.weekday()) # round down to last monday
    message = mail.EmailMessage(
        sender="mlambert@gmail.com", #TODO(lambert): fix this up to allow additional email addresses
        subject="Dance events for %s" % d.strftime('%b %d, %Y'),
        to=batch_lookup.data_for_user(user.fb_uid)['profile']['email'],
        html=rendered
    )
    message.send()

