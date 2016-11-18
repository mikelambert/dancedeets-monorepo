import logging
import re
from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors

from loc import gmaps_api
from loc import formatting
from util import abbrev

ONLINE_ADDRESS = 'ONLINE'

# TODO: do some auto-classification of ripley grier, pearl studios, champion studios, etc. People always type horrible addresses.
# UCI
# UCLB
# JD School
# V.D'ASCQ replacements? -> Villeneuve-d'Ascq
# detect obvious city names embedded inside?

# TODO(lambert): when we get an un-geocodable address, stick with last-known-address in the DBEvent, and do not overwrite with None


class LocationMapping(db.Model):
    remapped_address = db.StringProperty(indexed=False)


def city_for_fb_location(location):
    state = abbrev.states_full2abbrev.get(location.get('state'), location.get('state'))
    if location.get('city') and (state or location.get('country')):
        address_components = [location.get('city'), state, location.get('country')]
        address_components = [x for x in address_components if x]
        address = ', '.join(address_components)
        return address
    else:
        return None


def _get_latlng_from_event(fb_event):
    venue = fb_event['info'].get('venue')
    if venue and venue.get('latitude') and venue.get('longitude'):
        return float(venue['latitude']), float(venue['longitude'])
    # In the "olden days", we would get a venue block with an id but without a lat/lng, requiring further lookup.
    # We don't appear to get this any more, so we can eliminate our event-dependent venue lookup code.
    # Maybe we get an id and no lat/lng still, but looking up the latest venue information shouldn't give a lat/lng either.
    return None


def get_address_for_fb_event(fb_event):
    event_info = fb_event['info']
    venue = event_info.get('venue', {})
    event_location = event_info.get('location', '')

    # Sometimes the venue is [] instead of {...}, so handle that no-venue scenario
    if not venue:
        return event_location

    # Use states_full2abbrev to convert "Lousiana" to "LA" so "Hollywood, LA" geocodes correctly.
    state = abbrev.states_full2abbrev.get(venue.get('state'), venue.get('state'))
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
    location_mapping = LocationMapping.get_by_key_name(address)
    if location_mapping:
        return location_mapping.remapped_address
    else:
        return None


def _save_remapped_address_for(original_address, new_remapped_address):
    original_address = (original_address or '').strip()
    if new_remapped_address != ' ':
        new_remapped_address = (new_remapped_address or '').strip()
    if original_address:
        location_mapping = LocationMapping.get_by_key_name(original_address)
        if new_remapped_address:
            if not location_mapping:
                location_mapping = LocationMapping(key_name=original_address)
            location_mapping.remapped_address = new_remapped_address
            try:
                location_mapping.put()
            except apiproxy_errors.CapabilityDisabledError, e:
                logging.error("failed to save location mapping due to %s", e)
        else:
            if location_mapping:
                location_mapping.delete()


def update_remapped_address(fb_event, new_remapped_address):
    new_remapped_address = new_remapped_address or None
    location_info = LocationInfo(fb_event)
    logging.info("remapped address for fb_event %r, new form value %r", location_info.remapped_address, new_remapped_address)
    if location_info.remapped_address != new_remapped_address:
        _save_remapped_address_for(location_info.fb_address, new_remapped_address)


class LocationInfo(object):
    def __init__(self, fb_event=None, db_event=None, debug=False):
        self.exact_from_event = False
        self.overridden_address = None
        self.fb_address = None
        self.remapped_address = None
        self.final_address = None

        has_overridden_address = db_event and db_event.address
        if not has_overridden_address and not fb_event:
            logging.warning("Passed a db_event without an address, and no fb_event to pull from: %s" % db_event.id)
        if (not has_overridden_address and fb_event) or debug:
            self.final_latlng = _get_latlng_from_event(fb_event)
            if self.final_latlng:
                self.geocode = gmaps_api.lookup_latlng(self.final_latlng)
                self.fb_address = formatting.format_geocode(self.geocode)
                self.remapped_address = None
                self.exact_from_event = bool(self.geocode)
            # Sometimes the geocode above fails, so we fallback on addresses.
            # For exmaple: venue id 156028414450815 with latlng: (24.43012, 118.31452)
            if not self.geocode:
                self.fb_address = get_address_for_fb_event(fb_event)
                self.remapped_address = _get_remapped_address_for(self.fb_address)
                if self.remapped_address:
                    logging.info("Checking remapped address, which is %r", self.remapped_address)
            self.final_address = self.remapped_address or self.fb_address
        if has_overridden_address:
            self.overridden_address = db_event.address
            self.final_address = self.overridden_address

        if not self.exact_from_event:
            logging.info("Final address is %r", self.final_address)
            if self.online:
                self.geocode = None
            elif self.final_address is not None:
                self.geocode = gmaps_api.lookup_address(self.final_address)
            else:
                self.geocode = None

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
