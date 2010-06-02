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

        facebook_location = self.current_user()['profile']['location']['name']

        #TODO(lambert): fix default user creation in /login to also handle the information here
        defaults = {
            'location': facebook_location,
            'freestyle': users.FREESTYLE_FAN_NO_CLUBS,
            'choreo': users.CHOREO_FAN,
            'send_email': True,
            'distance': '60',
            'distance_units': 'km',
        }
        if self.user_country in locations.MILES_COUNTRIES:
            defaults['distance_units'] = 'miles'

        user = users.get_user(self.fb_uid)
        if user.fb_access_token:
            for k in defaults:
                defaults[k] = getattr(user, k)
        for field in defaults.keys():
            if self.request.get(field):
                defaults[field] = self.request.get(field)
        self.display['defaults'] = defaults

        # distance between saved location and facebook current location
        facebook_geo_location = locations.get_geocoded_location(facebook_location)['latlng']
        user_geo_location = locations.get_geocoded_location(defaults['location'])['latlng']
        distance = locations.get_distance(facebook_geo_location[0], facebook_geo_location[1], user_geo_location[0], user_geo_location[1])
        self.display['location_distance'] = distance
        self.display['facebook_location'] = facebook_location

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
