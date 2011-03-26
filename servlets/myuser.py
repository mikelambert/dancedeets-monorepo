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

        self.display['DANCE_TYPES_LIST'] = users.DANCE_TYPES_LIST

        defaults = {}
        user = users.User.get_by_key_name(str(self.fb_uid))
        for k in dir(user):
            defaults[k] = getattr(user, k)
        for field in defaults.keys():
            if self.request.get(field):
                defaults[field] = self.request.get(field)
        self.display['defaults'] = defaults

        location_too_far = False
        location_unknown = False

        #TODO(lambert): implement distance-from-saved-location and current-location better, via ajax and geo-api call

        self.render_template('user')

    def post(self):
        self.finish_preload()
        self.update_user()
        # Disabled due to an error: Only ancestor queries are allowed inside transactions.
        #db.run_in_transaction(self.update_user)
        self.user.add_message("Settings saved!")
        self.redirect('/')

    def update_user(self):
        user = users.User.get_by_key_name(str(self.fb_uid))
        for field in ['location', 'dance_type', 'distance_units', 'min_attendees']:
            form_value = self.request.get(field)
            setattr(user, field, form_value)
        user.distance = self.request.get('distance')
        if user.location:
            user.compute_derived_properties(self.batch_lookup.data_for_user(self.fb_uid))
            if not user.location_country:
                self.add_error("No country for location %r" % user.location)
            if not user.location_timezone:
                self.add_error("No timezone for location %r" % user.location)
        else:
            self.add_error("No location")
        #TODO(lambert): add an option for doing email "via facebook" as well. not everyone uses email.
        for field in ['send_email']:
            form_value = self.request.get(field) == "true"
            setattr(user, field, form_value)
        self.errors_are_fatal()
        user.put()
