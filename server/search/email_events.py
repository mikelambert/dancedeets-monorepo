import datetime
import logging

import app
import base_servlet
import fb_api
from mail import mandrill_api
import render_server
from servlets import api
from users import users
from util import fb_mapreduce
from . import search_base
from . import search

def email_for_user(user, fbl, should_send=True):
    if not user.send_email or not user.email:
        return
    if user.weekly_email_send_date and user.weekly_email_send_date > datetime.datetime.now() - datetime.timedelta(days=3):
        logging.warning("Skipping user %s (%s) because last weekly email was sent on %s", user.fb_uid, user.full_name, user.weekly_email_send_date)
        # Sent the weekly email too recently, let's abort
        return
    fb_user = fbl.fetched_data(fb_api.LookupUser, fbl.fb_uid)
    if not 'profile' in fb_user:
        return

    user_location = user.location
    if not user_location:
        return

    d = datetime.date.today()
    start_time = d - datetime.timedelta(days=d.weekday()) # round down to last monday
    end_time = start_time + datetime.timedelta(days=8)
    data = {
        'location': user_location,
        'distance': user.distance_in_km(),
        'distance_units': 'km',
        'start': start_time,
        'end': end_time,
    }
    form = search_base.SearchForm(data=data)

    city_name = None
    center_latlng = None
    southwest = None
    northeast = None
    if form.location.data:
        try:
            city_name, center_latlng, southwest, northeast = search_base.normalize_location(form)
        except:
            return 'Unknown location'

    search_query = form.build_query(start_end_query=True)
    search_results = search.Search(search_query).get_search_results()
    # Don't send email...
    if not search_results:
        return

    fb_user = fbl.fetched_data(fb_api.LookupUser, fbl.fb_uid)

    need_full_event = False
    json_search_response = api.build_search_results_api(user_location, form, search_query, search_results, (2, 0), need_full_event, center_latlng, southwest, northeast, skip_people=True)
    locale = user.locale or 'en_US'
    props = {
        'currentLocale': locale.replace('_', '-'),
        'user': {
            'userName': user.first_name or user.name or '',
        },
        'response': json_search_response,
    }
    response = render_server.render_jsx('weeklyMail.js', props, static_html=True)
    if response.error:
        logging.error('Error rendering weeklyMail.js: %s', response.error)
        return
    mjml_response = render_server.render_mjml(response.markup)
    rendered_html = mjml_response['html']
    if mjml_response.get('errors'):
        logging.error('Errors rendering weeklyMail.mjml: %s', mjml_response['errors'])
    subject = 'Dance events for %s' % d.strftime('%b %d, %Y')
    message = {
        'from_email': 'events@dancedeets.com',
        'from_name': 'DanceDeets Events',
        'subject': subject,
        'to': [{
            'email': user.email,
            'name': user.full_name or user.first_name or '',
            'type': 'to',
        }],
        'html': rendered_html,
        'metadata': {
            'user_id': user.fb_uid,
            'email_type': 'weekly',
        },
    }
    if should_send:
        # Update the last-sent-time here, so we any retryable errors don't cause emails to be multi-sent
        user = users.User.get_by_id(user.fb_uid)
        user.weekly_email_send_date = datetime.datetime.now()
        user.put()
        # And send the message now.
        mandrill_api.send_message(message)
    return message

@app.route('/tools/display_email')
class DisplayEmailHandler(base_servlet.UserOperationHandler):
    def user_operation(self, fbl, users):
        fbl.get(fb_api.LookupUser, users[0].fb_uid)
        message = email_for_user(users[0], fbl, should_send=False)
        if message:
            self.response.out.write(message['html'])
        else:
            self.response.out.write('Error generating mail html')


#TODO(lambert): do we really want yield on this one?
def yield_email_user(fbl, user):
    fbl.request(fb_api.LookupUser, user.fb_uid)
    fbl.request(fb_api.LookupUserEvents, user.fb_uid)
    try:
        fbl.batch_fetch()
    except fb_api.ExpiredOAuthToken as e:
        logging.info("Auth token now expired, mark as such: %s", e)
        user.expired_oauth_token_reason = e.args[0]
        user.expired_oauth_token = True
        user.put()
        return None
    try:
        email = email_for_user(user, fbl, should_send=True)
        return email
    except Exception as e:
        logging.exception("Error sending email for user %s", user.fb_uid)
        return None
map_email_user = fb_mapreduce.mr_user_wrap(yield_email_user)
email_user = fb_mapreduce.nomr_wrap(yield_email_user)

def mr_email_user(fbl):
    fb_mapreduce.start_map(
        fbl=fbl,
        name='Email Users',
        #TODO: MOVE
        handler_spec='search.email_events.map_email_user',
        entity_kind='users.users.User',
    )
