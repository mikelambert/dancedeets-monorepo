import base_servlet
import fb_api
from events import users

class UserHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()

        defaults = {}
        user = users.User.get_by_key_name(self.fb_uid)
        for k in dir(user):
            defaults[k] = getattr(user, k)
        for field in defaults.keys():
            if self.request.get(field):
                defaults[field] = self.request.get(field)
        self.display['defaults'] = defaults

        #location_too_far = False
        #location_unknown = False

        #TODO(lambert): implement distance-from-saved-location and current-location better, via ajax and geo-api call

        self.render_template('user')

    def post(self):
        self.finish_preload()
        self.update_user()
        # Disabled due to an error, the user.compute_derived_properties does some GeoCode lookups which are not ancestor queries.
        #db.run_in_transaction(self.update_user)
        self.user.add_message("Settings saved!")
        self.redirect('/')

    def update_user(self):
        user = users.User.get_by_key_name(self.fb_uid)
        for field in ['location', 'distance_units']:
            form_value = self.request.get(field)
            setattr(user, field, form_value)
        user.distance = self.request.get('distance')
        user.min_attendees = int(self.request.get('min_attendees'))
        if user.location:
            user.compute_derived_properties(self.fbl.fetched_data(fb_api.LookupUser, self.fb_uid))
            if not user.location_country:
                self.add_error("No country for location %r" % user.location)
        else:
            self.add_error("No location")
        #TODO(lambert): add an option for doing email "via facebook" as well. not everyone uses email.
        for field in ['send_email']:
            form_value = self.request.get(field) == "true"
            setattr(user, field, form_value)
        self.errors_are_fatal()
        user.put()
