import datetime
import logging
import re

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

class NoEmailException(Exception):
    pass

def email_for_user(user, fbl, should_send=True):
    if not user.send_email:
        raise NoEmailException('User has send_email==False')
    if not user.email:
        raise NoEmailException('User does not have an email')

    if user.weekly_email_send_date and user.weekly_email_send_date > datetime.datetime.now() - datetime.timedelta(days=3):
        message = "Skipping user %s (%s) because last weekly email was sent on %s" % (user.fb_uid, user.full_name, user.weekly_email_send_date)
        logging.warning(message)
        # Sent the weekly email too recently, let's abort
        raise NoEmailException(message)
    fb_user = fbl.fetched_data(fb_api.LookupUser, fbl.fb_uid)
    if not 'profile' in fb_user:
        raise NoEmailException('Could not find LookupUser: %s', fb_user)

    user_location = user.location
    if not user_location:
        raise NoEmailException('User does not have location')

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
        except Exception as e:
            raise NoEmailException('Could not normalize user location: %s: %s', data, e)

    try:
        search_query = form.build_query(start_end_query=True)
    except:
        logging.error('Error looking up user location for user %s, form: %s', user.fb_uid, form)
        raise
    search_results = search.Search(search_query).get_search_results()
    # Don't send email...
    if not search_results:
        raise NoEmailException('No search results for user')

    fb_user = fbl.fetched_data(fb_api.LookupUser, fbl.fb_uid)

    need_full_event = False
    json_search_response = api.build_search_results_api(user_location, form, search_query, search_results, (2, 0), need_full_event, center_latlng, southwest, northeast, skip_people=True)
    locale = user.locale or 'en_US'
    props = {
        'currentLocale': locale.replace('_', '-'),
        'user': {
            'userName': user.first_name or user.full_name or '',
        },
        'response': json_search_response,
    }
    response = render_server.render_jsx('weeklyMail.js', props, static_html=True)
    if response.error:
        message = 'Error rendering weeklyMail.js: %s' % response.error
        logging.error(message)
        raise NoEmailException(message)
    mjml_response = render_server.render_mjml(response.markup)
    rendered_html = mjml_response['html']
    if mjml_response.get('errors'):
        message = 'Errors rendering weeklyMail.mjml: %s', mjml_response['errors']
        logging.error(message)
        raise NoEmailException(message)
    messages = [
        'Your Week in Dance: %s',
        'DanceDeets Weekly: %s',
        'Dance Events for %s',
    ]
    message = random.choice(messages)

    tag = re.sub(r'[^a-z]', '-', message.lower())[:50]
    tags = [
        'weekly',
        tag,
    ]

    subject = message % d.strftime('%b %d, %Y')
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
        'tags': tags,
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
        try:
            message = email_for_user(users[0], fbl, should_send=False)
        except Exception as e:
            self.response.out.write('Error generating mail html: %s', e)
        else:
            self.response.out.write(message['html'])


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
    except NoEmailException as e:
        logging.info("Not sending email for user %s: %s", user.fb_uid, e)
        return None
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
