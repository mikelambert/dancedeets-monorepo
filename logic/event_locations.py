import logging
import re
from google.appengine.ext import db
import fb_api

from events import cities
import locations
from util import abbrev

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

def _get_latlng_from_event(batch_lookup, fb_event):
    event_info = fb_event['info']
    venue = event_info.get('venue', {}) #TODO(lambert): need to support "venue decoration" so we don't need to do one-by-one lookups here
    # if we have a venue id, get the city from there
    logging.info("venue id is %s", venue.get('id'))
    if venue.get('latitude') and venue.get('longitude'):
        return float(venue['latitude']), float(venue['longitude'])
    if venue.get('id'):
        batch_lookup = batch_lookup.copy(allow_cache=batch_lookup.allow_cache)
        batch_lookup.lookup_venue(venue.get('id'))
        batch_lookup.finish_loading()
        venue_data = batch_lookup.data_for_venue(venue.get('id'))
        if venue_data['deleted']:
            logging.warning("no venue found for event id %s, venue id %s, retrying with cache bust", fb_event['info'].get('id'), venue.get('id'))
            # TODO(lambert): clean up old venues in the system, this is a hack until then
            batch_lookup = batch_lookup.copy(allow_cache=False)
            batch_lookup.lookup_venue(venue.get('id'))
            batch_lookup.finish_loading()
            venue_data = batch_lookup.data_for_venue(venue.get('id'))
            if venue_data['deleted']:
                logging.error("STILL no venue found for id %s, giving up", venue.get('id'))
        if not venue_data['deleted']:
            loc = (venue_data['info'].get('location', {}))
            return float(loc['latitude']), float(loc['longitude'])
    return None

def get_address_for_fb_event(fb_event):
    event_info = fb_event['info']
    venue = event_info.get('venue', {})
    event_location = event_info.get('location')

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
    #TODO(lambert): How about we have a sharded-memcache-key based on first hexadecimal character of md5-hash of address. this key-value would store all re-mappings with that prefix, and could be db-and-memcached easily.
    #TODO(lambert): Write a mapreduce which goes through events looking for unnecessary mappings to clear out the mapping space.
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

def update_remapped_address(batch_lookup, fb_event, new_remapped_address):
    new_remapped_address = new_remapped_address or None
    location_info = LocationInfo(batch_lookup, fb_event)
    logging.info("remapped address for fb_event %r, new form value %r", location_info.remapped_address, new_remapped_address)
    if location_info.remapped_address != new_remapped_address:
        _save_remapped_address_for(location_info.fb_address, new_remapped_address)


ONLINE_ADDRESS = 'ONLINE'
def get_city_name_and_latlng(address=None):
    if address == ONLINE_ADDRESS:
        return ONLINE_ADDRESS, None
    else:
        return locations.get_city_name_and_latlng(address=address)

class LocationInfo(object):
    def __init__(self, batch_lookup, fb_event, db_event=None, debug=False):
        has_overridden_address = db_event and db_event.address

        self.exact_from_event = False
        self.overridden_address = None
        self.fb_address = None
        self.remapped_address = None
        if not has_overridden_address or debug:
            self.final_latlng = _get_latlng_from_event(batch_lookup, fb_event)
            if self.final_latlng:
                self.exact_from_event = True
                self.final_city = locations.get_city_name(latlng=self.final_latlng)
                self.fb_address = self.final_city
                self.remapped_address = None
            else:
                self.fb_address = get_address_for_fb_event(fb_event)
                self.remapped_address = _get_remapped_address_for(self.fb_address)
                if self.remapped_address:
                    logging.info("Checking remapped address, which is %r", self.remapped_address)
                result = get_city_name_and_latlng(address=self.remapped_address or self.fb_address)
                if result:
                    self.final_city, self.final_latlng = result
                else:
                    self.final_city = None
                    self.final_latlng = None

        if has_overridden_address:
            self.overridden_address = db_event.address
            logging.info("Address overridden to be %r", self.overridden_address)
            result = get_city_name_and_latlng(address=self.overridden_address)
            if result:
                self.final_city, self.final_latlng = result
            else:
                self.final_city = None
                self.final_latlng = None

        logging.info("Final latlng is %r, final city is %r", self.final_latlng, self.final_city)

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

    def largest_nearby_city(self):
        if self.is_online_event():
            return None
        else:
            return cities.get_largest_nearby_city_name(self.final_city) #TODO(lambert): switch this to latlng lookup

    def latlong(self):
        if self.is_online_event():
            return None, None
        else:
            return self.final_latlng

