import collections
import csv

import base_servlet
import fb_api
from . import users

class UserHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()

        defaults = {}
        user = users.User.get_by_id(self.fb_uid)
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
        user = users.User.get_by_id(self.fb_uid)
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

class ShowUsersHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        num_fetch_users = int(self.request.get('num_users', 500))
        order_field = self.request.get('order_field', 'creation_time')
        all_users = users.User.query().order(-getattr(users.User, order_field)).fetch(num_fetch_users)
        client_counts = collections.defaultdict(lambda: 0)
        for user in all_users:
            for client in user.clients:
                client_counts[client] += 1
        user_ids = [x.fb_uid for x in all_users]
        fb_users = self.fbl.get_multi(fb_api.LookupUser, user_ids)

        self.display['client_counts'] = client_counts
        self.display['num_users'] = len(all_users)
        self.display['num_active_users'] = len([x for x in all_users if not x.expired_oauth_token])
        self.display['users'] = all_users
        self.display['fb_users'] = fb_users
        self.display['track_google_analytics'] = False
        self.render_template('show_users')

class UserEmailExportHandler(base_servlet.BaseRequestHandler):
    def get(self):
        num_fetch_users = int(self.request.get('num_users', 500))
        order_field = self.request.get('order_field', 'creation_time')
        all_users = users.User.query().order(-getattr(users.User, order_field)).fetch(num_fetch_users)
        writer = csv.writer(self.response.out)
        for user in all_users:
            if user.email:
                writer.writerow([user.email.encode('utf8'), (user.full_name or '').encode('utf8')])
