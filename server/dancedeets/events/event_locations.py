import logging
import pycountry
import re
import time

from google.cloud import ndb

from dancedeets.event_attendees import person_city
from dancedeets.loc import gmaps_api
from dancedeets.loc import formatting
from dancedeets.util import fb_events
from dancedeets.util import timelog

ONLINE_ADDRESS = 'ONLINE'

# TODO: do some auto-classification of ripley grier, pearl studios, champion studios, etc. People always type horrible addresses.
# UCI
# UCLB
# JD School
# V.D'ASCQ replacements? -> Villeneuve-d'Ascq
# detect obvious city names embedded inside?

# TODO(lambert): when we get an un-geocodable address, stick with last-known-address in the DBEvent, and do not overwrite with None


class LocationMapping(ndb.Model):
    remapped_address = ndb.StringProperty(indexed=False)


def state_name_for_fb_location(location):
    state_name = location.get('state')
    try:
        country = pycountry.countries.get(name=location.get('country'))
        state = pycountry.subdivisions.get(code='%s-%s' % (country.alpha_2, location.get('state')))
        if state:
            state_name = state.name
    except KeyError:
        pass
    return state_name


def city_for_fb_location(location):
    state = state_name_for_fb_location(location)
    if location.get('city') and (state or location.get('country')):
        address_components = [location.get('city'), state, location.get('country')]
        address_components = [x for x in address_components if x]
        address = ', '.join(address_components)
        return address
    else:
        return None


def get_fb_place(fb_event):
    event_info = fb_event['info']
    place = event_info.get('place', {}).get(
        'location',
        # bwcompat:
        event_info.get('venue', {}) or {}
    )
    return place


def get_fb_place_name(fb_event):
    event_info = fb_event['info']
    event_location = event_info.get('place', {}).get(
        'name',
        # bwcompat:
        event_info.get('location', None)
    )
    return event_location


def get_fb_place_id(fb_event):
    event_info = fb_event['info']
    event_location = event_info.get('place', {}).get(
        'id',
        # bwcompat:
        (event_info.get('venue', {}) or {}).get('id', None)
    )
    return event_location


def _get_latlng_from_event(fb_event):
    venue = get_fb_place(fb_event)
    if venue and venue.get('latitude') and venue.get('longitude'):
        return float(venue['latitude']), float(venue['longitude'])
    # In the "olden days", we would get a venue block with an id but without a lat/lng, requiring further lookup.
    # We don't appear to get this any more, so we can eliminate our event-dependent venue lookup code.
    # Maybe we get an id and no lat/lng still, but looking up the latest venue information shouldn't give a lat/lng either.
    return None


def get_address_for_fb_event(fb_event):
    venue = get_fb_place(fb_event)
    event_location = get_fb_place_name(fb_event)

    # Sometimes the venue is [] instead of {...}, so handle that no-venue scenario
    if not venue:
        return event_location

    state = state_name_for_fb_location(venue)
    address_components = [event_location, venue.get('street'), venue.get('city'), state, venue.get('country')]
    address_components = [x for x in address_components if x]
    final_address = ', '.join(address_components)

    # many geocodes have a couple trailing digits, a la "VIA ROMOLO GESSI 14"
    return re.sub(r' \d{,3}$', '', final_address)


def _get_remapped_address_for(address):
    address = (address or '').strip()
    if not address:
        return None
    # map locations to corrected locations for events that have wrong or incomplete info
    # TODO(lambert): How about we have a sharded-memcache-key based on first hexadecimal character of md5-hash of address. this key-value would store all re-mappings with that prefix, and could be db-and-memcached easily.
    # TODO(lambert): Write a mapreduce which goes through events looking for unnecessary mappings to clear out the mapping space.
    location_mapping = LocationMapping.get_by_id(address)
    if location_mapping:
        return location_mapping.remapped_address
    else:
        return None


def _save_remapped_address_for(original_address, new_remapped_address):
    original_address = (original_address or '').strip()
    if new_remapped_address != ' ':
        new_remapped_address = (new_remapped_address or '').strip()
    if original_address:
        location_mapping = LocationMapping.get_by_id(original_address)
        if new_remapped_address:
            if not location_mapping:
                location_mapping = LocationMapping(id=original_address)
            location_mapping.remapped_address = new_remapped_address
            try:
                location_mapping.put()
            except Exception as e:
                logging.error("failed to save location mapping due to %s", e)
        else:
            if location_mapping:
                location_mapping.key.delete()


def update_remapped_address(fb_event, new_remapped_address):
    new_remapped_address = new_remapped_address or None
    location_info = LocationInfo(fb_event)  # only doing this to look up the old remapped address
    logging.info("remapped address for fb_event %r, new form value %r", location_info.remapped_address, new_remapped_address)
    if location_info.remapped_address != new_remapped_address:
        _save_remapped_address_for(location_info.fb_address, new_remapped_address)


class LocationInfo(object):
    def __init__(self, fb_event=None, fb_event_attending_maybe=None, db_event=None, debug=False, check_places=True):
        self.overridden_address = None
        self.fb_address = None
        self.remapped_address = None
        self.final_address = None
        self.geocode = None

        # If we're not doing a full-fledged step-by-step debug, used our cached geocode (if available)
        if not debug and db_event and db_event.has_geocode():
            self.geocode = db_event.get_geocode()
            self.final_address = self.geocode.formatted_address()
            # Sometimes we get called with a webevent...in which case the fb_address doesn't matter
            if db_event.fb_event:
                self.fb_address = get_address_for_fb_event(db_event.fb_event)
            return

        has_overridden_address = db_event and db_event.address
        if not has_overridden_address and not fb_event:
            logging.warning("Passed a db_event without an address, and no fb_event to pull from: %s" % db_event.id)
        if (not has_overridden_address and fb_event) or debug:
            # We try to trust the address *over* the latlong,
            # because fb uses bing which has less accuracy on some addresses (ie a jingsta address)
            self.fb_address = get_address_for_fb_event(fb_event)
            logging.info('fb address is %s', self.fb_address)
            self.remapped_address = _get_remapped_address_for(self.fb_address)
            if self.remapped_address:
                logging.info("Checking remapped address, which is %r", self.remapped_address)
            lookup_address = self.remapped_address or self.fb_address
            if lookup_address:
                location_geocode = gmaps_api.lookup_string(lookup_address, check_places=check_places)
                if location_geocode:
                    self.geocode = location_geocode
                    self.final_address = location_geocode.formatted_address()
            if not self.geocode:
                self.final_latlng = _get_latlng_from_event(fb_event)
                if self.final_latlng:
                    self.geocode = gmaps_api.lookup_latlng(self.final_latlng)
                    self.fb_address = formatting.format_geocode(self.geocode)

            self.final_address = self.final_address or self.remapped_address or self.fb_address
        if has_overridden_address:
            self.geocode = None
            self.overridden_address = db_event.address
            self.final_address = self.overridden_address
            if self.final_address != ONLINE_ADDRESS:
                self.geocode = gmaps_api.lookup_string(self.final_address, check_places=check_places)

        if fb_event_attending_maybe:
            ids = fb_events.get_event_attendee_ids(fb_event_attending_maybe)
            start = time.time()
            self.attendee_based_city = person_city.get_top_city_for(ids)
            event_id = db_event.id if db_event else fb_event['info']['id']
            timelog.log_time_since('Guessing Location for Event %s with %s Attendee IDs' % (event_id, len(ids)), start)

            if not self.geocode and self.attendee_based_city:
                logging.info('No geocode found, but we have an attendee_geoname_id pointing to %s, using that', self.attendee_based_city)
                self.final_address = self.attendee_based_city
                self.geocode = gmaps_api.lookup_string(self.final_address, check_places=check_places)

        logging.info("Final address is %r", self.final_address)

    @property
    def online(self):
        return self.final_address == ONLINE_ADDRESS

    @property
    def final_city(self):
        if self.geocode:
            return formatting.format_geocode(self.geocode)
        elif self.online:
            return ONLINE_ADDRESS
        else:
            return None

    def needs_override_address(self):
        address = self.remapped_address or self.fb_address or ''
        trimmed_address = address.replace('.', '').replace(' ', '').upper()
        return (trimmed_address in ['TBA', 'TBD', ''])

    def is_online_event(self):
        return self.final_city == ONLINE_ADDRESS

    def actual_city(self):
        if self.is_online_event():
            return None
        else:
            return self.final_city

    def latlong(self):
        if self.geocode:
            return self.geocode.latlng()
        else:
            return None, None
