#!/usr/bin/env python
import logging
from google.appengine.ext import db

import base_servlet
import locations
from events import cities
from events import users

class UserHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()

        self.display['DANCES'] = users.DANCES
        self.display['DANCE_HEADERS'] = users.DANCE_HEADERS
        self.display['DANCE_LISTS'] = users.DANCE_LISTS

        defaults = {}
        for k in dir(self.user):
            defaults[k] = getattr(self.user, k)
        for field in defaults.keys():
            if self.request.get(field):
                defaults[field] = self.request.get(field)
        self.display['defaults'] = defaults

        location_too_far = False
        location_unknown = False

        facebook_location = users.get_location(self.current_user())
        # distance between saved location and facebook current location
        if facebook_location:
            facebook_geo_location = locations.get_geocoded_location(facebook_location)['latlng']
            user_geo_location = locations.get_geocoded_location(defaults['location'])['latlng']
            distance = locations.get_distance(facebook_geo_location[0], facebook_geo_location[1], user_geo_location[0], user_geo_location[1])
            if distance > 100:
                location_too_far = True
        if not self.user.location:
            location_unknown = True
        self.display['location_too_far'] = location_too_far
        self.display['location_unknown'] = location_unknown
        self.display['facebook_location'] = facebook_location or "Unknown"

        self.render_template('user')

    def post(self):
        self.update_user()
        # Disabled due to an error: Only ancestor queries are allowed inside transactions.
        #db.run_in_transaction(self.update_user)
        self.redirect('/user/edit')

    def update_user(self):
        user = users.User.get(self.fb_uid, self.request.get('location'))
        for field in ['location', 'freestyle', 'choreo', 'distance_units']:
            form_value = self.request.get(field)
            setattr(user, field, form_value)
        user.distance = self.request.get('distance')
        if user.location:
            country = locations.get_country_for_location(user.location)
            geocoded_location = locations.get_geocoded_location(user.location)
            user.location_country = country
            user.location_timezone = cities.get_closest_city(user.location).timezone
            if not user.location_country:
                self.add_error("No country for location %r" % location_name)
            if not user.location_timezone:
                self.add_error("No timezone for location %r" % location_name)
        else:
            self.add_error("No location")
        for field in ['send_email']:
            form_value = self.request.get(field) == "true"
            setattr(user, field, form_value)
        self.errors_are_fatal()
        user.put()
