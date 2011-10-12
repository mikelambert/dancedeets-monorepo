import logging
from google.appengine.ext import db
import fb_api

from events import cities
import locations
from util import abbrev

class LocationMapping(db.Model):
    remapped_address = db.StringProperty()

def _city_for_venue(venue):
    # Use states_full2abbrev to convert "Lousiana" to "LA" so "Hollywood, LA" geocodes correctly.
    state = abbrev.states_full2abbrev.get(venue.get('state'), venue.get('state'))
    if venue.get('city') and (state or venue.get('country')):
        address_components = [venue.get('city'), state, venue.get('country')]
        address_components = [x for x in address_components if x]
        address = ', '.join(address_components)
        return address
    else:
        return None

def _address_for_venue(venue, raw_location):
    # Use states_full2abbrev to convert "Lousiana" to "LA" so "Hollywood, LA" geocodes correctly.
    state = abbrev.states_full2abbrev.get(venue.get('state'), venue.get('state'))
    address_components = [raw_location, venue.get('street'), venue.get('city'), state, venue.get('country')]
    address_components = [x for x in address_components if x]
    address = ', '.join(address_components)
    return address

def _get_city_for_fb_event(fb_event):
    event_info = fb_event['info']
    venue = event_info.get('venue', {})
    # if we have a venue id, get the city from there
    logging.info("venue id is %s", venue.get('id'))
    if venue.get('id'):
        # TODO(lambert): need a better way to pass in a proper fb auth token here, so that we aren't bucked into common ip set
        batch_lookup = fb_api.CommonBatchLookup(None, None)
        batch_lookup.lookup_venue(venue.get('id'))
        batch_lookup.finish_loading()
        venue_data = batch_lookup.data_for_venue(venue.get('id'))
        if not venue_data['deleted']:
            logging.info("venue data is %s", venue_data)
            city = _city_for_venue(venue_data['info'].get('location', {}))
            logging.info("venue address is %s", city)
            if city:
                return city
    # otherwise fall back on the address in the event, and go from there
    city = _city_for_venue(venue)
    if city:
        return city
    else:
        return None

def _get_address_for_fb_event(fb_event):
    event_info = fb_event['info']
    venue = event_info.get('venue', {})
    raw_location = event_info.get('location')
    return _address_for_venue(venue, raw_location=raw_location)

def _get_remapped_address_for(address):
    if not address:
        return ''
    # map locations to corrected locations for events that have wrong or incomplete info
    location_mapping = LocationMapping.get_by_key_name(address)
    if location_mapping:
        return location_mapping.remapped_address
    else:
        return None

def _save_remapped_address_for(original_address, new_remapped_address):
    if original_address:
        location_mapping = LocationMapping.get_or_insert(original_address)
        if new_remapped_address:
            location_mapping.remapped_address = new_remapped_address
            try:
                location_mapping.put()
            except apiproxy_errors.CapabilityDisabledError:
                pass
        else:
            location_mapping.delete()

def update_remapped_address(fb_event, new_remapped_address):
    new_remapped_address = new_remapped_address or None
    location_info = event_locations.LocationInfo(fb_event)
    logging.info("remapped address for fb_event %r, new form value %r", location_info.remapped_address, new_remapped_address)
    if location_info.remapped_address != new_remapped_address:
        _save_remapped_address_for(location_info.fb_address, new_remapped_address)


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

        if db_event and db_event.address:
            self.overridden_address = db_event.address
            self.remapped_address = None
            self.final_address = self.overridden_address
            logging.info("Address overridden to be %r", db_event.address)
        else:
            self.overridden_address = None
            if not self.fb_city:
                self.remapped_address = _get_remapped_address_for(self.fb_address)
                if self.remapped_address:
                    self.final_address = self.remapped_address
                else:
                    self.final_address = self.fb_address
                logging.info("No fb city, so checking remapped address, which is %r", self.remapped_address)
            else:
                self.remapped_address = None
                self.final_address = self.fb_city
        results = locations.get_geocoded_location(self.final_address)
        self.final_city = results['city']
        self.final_latlng = results['latlng']
        logging.info("Final address is %r, final city is %r", self.final_address, self.final_city)

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

