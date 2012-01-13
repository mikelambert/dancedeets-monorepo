import logging
import re
from google.appengine.ext import db
import fb_api

from events import cities
import locations
from util import abbrev

class LocationMapping(db.Model):
    remapped_address = db.StringProperty(indexed=False)

def city_for_fb_location(location):
    # Use states_full2abbrev to convert "Lousiana" to "LA" so "Hollywood, LA" geocodes correctly.
    state = abbrev.states_full2abbrev.get(location.get('state'), location.get('state'))
    if location.get('city') and (state or location.get('country')):
        address_components = [location.get('city'), state, location.get('country')]
        address_components = [x for x in address_components if x]
        address = ', '.join(address_components)
        return address
    else:
        return None

def venue_for_fb_location(location):
    returned_location = city_for_fb_location(location)
    if location.get('street'):
        returned_location = '%s, %s' % (location.get('street'), returned_location)
    else:
        return returned_location

def _address_for_venue(venue, raw_location):
    # Use states_full2abbrev to convert "Lousiana" to "LA" so "Hollywood, LA" geocodes correctly.
    state = abbrev.states_full2abbrev.get(venue.get('state'), venue.get('state'))
    address_components = [raw_location, venue.get('street'), venue.get('city'), state, venue.get('country')]
    address_components = [x for x in address_components if x]
    address = ', '.join(address_components)
    return address

def _get_city_for_fb_event(fb_event):
    event_info = fb_event['info']
    venue = event_info.get('venue', {}) #TODO(lambert): need to support "venue decoration" so we don't need to do one-by-one lookups here
    # if we have a venue id, get the city from there
    logging.info("venue id is %s", venue.get('id'))
    if venue.get('id'):
        # TODO(lambert): need a better way to pass in a proper fb auth token here, so that we aren't bucked into common ip set
        batch_lookup = fb_api.CommonBatchLookup(None, None)
        batch_lookup.lookup_venue(venue.get('id'))
        batch_lookup.finish_loading()
        venue_data = batch_lookup.data_for_venue(venue.get('id'))
        if not venue_data['deleted']:
            city = city_for_fb_location(venue_data['info'].get('location', {}))
            logging.info("venue address is %s", city)
            if city:
                return city
    # otherwise fall back on the address in the event, and go from there
    city = city_for_fb_location(venue)
    if city:
        return city
    else:
        return None

def _get_address_for_fb_event(fb_event):
    event_info = fb_event['info']
    venue = event_info.get('venue', {})
    raw_location = event_info.get('location')
    final_address = _address_for_venue(venue, raw_location=raw_location)
    # many geocodes have a couple trailing digits, a la "VIA ROMOLO GESSI 14"
    return re.sub(r' \d{,3}$', '', final_address)

def _get_remapped_address_for(address):
    if not address:
        return ''
    # map locations to corrected locations for events that have wrong or incomplete info
    #TODO(lambert): How about we have a sharded-memcache-key based on first hexadecimal character of md5-hash of address. this key-value would store all re-mappings with that prefix, and could be db-and-memcached easily.
    #TODO(lambert): Write a mapreduce which goes through events looking for unnecessary mappings to clear out the mapping space.
    location_mapping = LocationMapping.get_by_key_name(address)
    if location_mapping:
        return location_mapping.remapped_address
    else:
        return None

def _save_remapped_address_for(original_address, new_remapped_address):
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
        _save_remapped_address_for(location_info.remapped_source(), new_remapped_address)


ONLINE_ADDRESS = 'ONLINE'

class LocationInfo(object):
    def __init__(self, fb_event, db_event=None):
        # Do not trust facebook for latitude/longitude data. It appears to treat LA as Louisiana, etc. So always geocode
        self.fb_city = _get_city_for_fb_event(fb_event)
        if self.fb_city:
            self.fb_address = self.fb_city
        else:
            self.fb_address = _get_address_for_fb_event(fb_event)
    
        logging.info("For event %s, fb city is %r, fb address is %r", fb_event['info']['id'], self.fb_city, self.fb_address)

        # technically not needed for final location, but loaded here so we can still display on admin_edit page and modify it indepenently
        self.remapped_address = _get_remapped_address_for(self.remapped_source())
        if db_event and db_event.address:
            self.overridden_address = db_event.address
            self.final_address = self.overridden_address
            logging.info("Address overridden to be %r", db_event.address)
        else:
            self.overridden_address = None
            if self.remapped_address:
                self.final_address = self.remapped_address
                logging.info("Checking remapped address, which is %r", self.remapped_address)
            elif self.fb_city:
                self.final_address = self.fb_city
            else:
                self.final_address = self.fb_address
        results = locations.get_geocoded_location(self.final_address)
        self.final_city = results['city']
        self.final_latlng = results['latlng']
        logging.info("Final address is %r, final city is %r", self.final_address, self.final_city)

    def remapped_source(self):
        return self.fb_city or self.fb_address

    def needs_override_address(self):
        address = self.final_address or ''
        trimmed_address = address.replace('.', '').replace(' ', '').upper()
        return (trimmed_address in ['TBA', 'TBD', ''])

    def is_online_event(self):
        return self.final_address == ONLINE_ADDRESS

    def actual_city(self):
        if self.is_online_event():
            return None
        else:
            return self.final_city

    def largest_nearby_city(self):
        if self.is_online_event():
            return None
        else:
            return cities.get_largest_nearby_city_name(self.final_city)

    def latlong(self):
        if self.is_online_event():
            return None, None
        else:
            return self.final_latlng

