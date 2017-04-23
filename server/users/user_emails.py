import csv

import app
import base_servlet
from mail import mailchimp_api
from . import users

@app.route('/tools/user_emails')
class UserEmailExportHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        num_fetch_users = int(self.request.get('num_users', 500))
        order_field = self.request.get('order_field', 'creation_time')
        all_users = users.User.query().order(-getattr(users.User, order_field)).fetch(num_fetch_users)
        writer = csv.writer(self.response.out)
        writer.writerow(['Email', 'Full Name', 'First Name', 'Last Name', 'Expired Token', 'Weekly Subscription', 'Locale', 'Country'])
        for user in all_users:
            if user.email:
                trimmed_locale = user.locale or ''
                if '_' in trimmed_locale:
                    trimmed_locale = trimmed_locale.split('_')[0]
                writer.writerow([
                    user.email.encode('utf8'),
                    (user.full_name or '').encode('utf8'),
                    (user.first_name or '').encode('utf8'),
                    (user.last_name or '').encode('utf8'),
                    unicode(user.expired_oauth_token),
                    unicode(user.send_email),
                    trimmed_locale,
                    user.location_country or '',
                    ])

@app.route('/tools/export_to_mailchimp')
class ExportUsersHandler(base_servlet.BaseRequestHandler):
    def get(self):
        list_id = mailchimp.get_list_id()

members = [
    {
        "email_address": "mlambert@gmail.com",
        "status": "subscribed",
        "merge_fields": {
            "FIRSTNAME": "Mike",
            "LASTNAME": "Lambert",
            "NAME": "Mike Lambert",
        }
    }
]
