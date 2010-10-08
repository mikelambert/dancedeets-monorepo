import datetime
import logging

from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.runtime import apiproxy_errors

from events import eventdata
from events import tags
import fb_api
import locations
from logic import event_classifier
from logic import rsvp
from logic import search
import template
from util import text

def get_potential_dance_events(batch_lookup, user):
    results_json = batch_lookup.data_for_user(user.fb_uid)['all_event_info']
    events = sorted(results_json, key=lambda x: x['start_time'])
    second_batch_lookup = fb_api.CommonBatchLookup(batch_lookup.fb_uid, batch_lookup.fb_graph)
    for mini_fb_event in events:
        second_batch_lookup.lookup_event(str(mini_fb_event['eid']))
    second_batch_lookup.finish_loading()
    dance_event_ids = []
    for mini_fb_event in events:
        fb_event = second_batch_lookup.data_for_event(mini_fb_event['eid'])
        is_dance_event = event_classifier.is_dance_event(fb_event)
        if is_dance_event:
            dance_event_ids.append(str(mini_fb_event['eid']))
    # ideally would use keys_only=True, but that's not supported on get_by_key_name :-/
    found_events = eventdata.DBEvent.get_by_key_name(dance_event_ids)
    found_event_ids = [x.key().name() for x in found_events if x]
    new_dance_event_ids = set(dance_event_ids).difference(found_event_ids)
    new_dance_events = [second_batch_lookup.data_for_event(x) for x in new_dance_event_ids]
    new_dance_events = sorted(new_dance_events, key=lambda x: x['info']['start_time'])
    return new_dance_events

class PotentialEvent(db.Model):
    looked_at = db.BooleanProperty()

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
    rsvp.decorate_with_rsvps(batch_lookup, search_results)
    past_results, present_results, grouped_results = search.group_results(search_results)
    # Don't include results more than a month out in these emails
    grouped_results = [x for x in grouped_results if x.id != 'year_events']

    # check the events user-was-invited-to, looking for any dance-related fb events we don't know about yet
    new_dance_events = get_potential_dance_events(batch_lookup, user)
    for event in new_dance_events:
        pe = PotentialEvent.get_or_insert(str(event['info']['id']))
        # saves it, with potentially false 'looked_at' field (unless already set as true by myself)
        if pe.looked_at is None:
            pe.looked_at = False
            try:
                pe.put()
            except apiproxy_errors.CapabilityDisabledError:
                pass

    display = {}
    display['date_human_format'] = user.date_human_format
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

