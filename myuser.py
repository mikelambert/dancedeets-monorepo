#!/usr/bin/env python

import base_servlet
import locations
from events import users

#TODO(lambert): send weekly emails with upcoming events per person
#TODO(lambert): check if they've created any events with dance, hiphop, etc in the name, and if so ask them to add the event to this site
#TODO(lambert): send notifications to interested users when someone adds a new event?

        
class UserHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()

        self.display['DANCES'] = users.DANCES
        self.display['DANCE_HEADERS'] = users.DANCE_HEADERS
        self.display['DANCE_LISTS'] = users.DANCE_LISTS

        defaults = {
            'location': self.current_user()['profile']['location']['name'],
            'freestyle': users.FREESTYLE_FAN_NO_CLUBS,
            'choreo': users.CHOREO_FAN,
            'send_email': True,
            'distance': '60',
            'distance_units': 'km',
        }
        if self.user_country in locations.MILES_COUNTRIES:
            defaults['distance_units'] = 'miles'

        user = users.get_user(self.fb_uid)
        for k in defaults:
            defaults[k] = getattr(user, k)
        for field in defaults.keys():
            if self.request.get(field):
                defaults[field] = self.request.get(field)
        self.display['defaults'] = defaults
        self.display['location'] = self.current_user()['profile']['location']['name']
        self.render_template('user')

    def post(self):
        user = users.get_user(self.fb_uid)
        for field in ['location', 'freestyle', 'choreo', 'distance', 'distance_units']:
            form_value = self.request.get(field)
            setattr(user, field, form_value)
        for field in ['send_email']:
            form_value = self.request.get(field) == "true"
            setattr(user, field, form_value)
        user.put()
        self.redirect('/user/edit')
