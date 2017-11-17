import logging
import re
import urllib
from dancedeets import fb_api
from dancedeets import render_server
from dancedeets.loc import names
from dancedeets.logic import mobile
from dancedeets.mail import mandrill_api


class NoEmailException(Exception):
    pass


def email_for_user(user, fbl, should_send=False):
    if not user.send_email:
        raise NoEmailException('User has send_email==False')
    email_address = user.email
    if not email_address:
        raise NoEmailException('User does not have an email')

    fb_user = fbl.fetched_data(fb_api.LookupUser, fbl.fb_uid)
    if not 'profile' in fb_user:
        raise NoEmailException('Could not find LookupUser: %s', fb_user)

    locale = user.locale or 'en_US'
    email_unsubscribe_url = 'https://www.dancedeets.com/user/unsubscribe?email=%s' % urllib.quote(email_address)
    props = {
        'user': {
            'userName': user.first_name or user.full_name or '',
            'city': user.city_name,
            'countryName': names.get_country_name(user.location_country),
        },
        'currentLocale': locale.replace('_', '-'),
        'mobileIosUrl': mobile.IOS_URL,
        'mobileAndroidUrl': mobile.ANDROID_URL,
        'emailPreferencesUrl': email_unsubscribe_url,
    }
    email_template = 'mailNewUser.js'
    response = render_server.render_jsx(email_template, props, static_html=True)
    if response.error:
        message = 'Error rendering mailNewUser.js: %s' % response.error
        logging.error(message)
        raise NoEmailException(message)
    mjml_response = render_server.render_mjml(response.markup)
    rendered_html = mjml_response['html']
    if mjml_response.get('errors'):
        message = 'Errors rendering mailNewUser.mjml: %s', mjml_response['errors']
        logging.error(message)
        raise NoEmailException(message)

    subject = 'Welcome to DanceDeets'

    tags = [
        'new-user',
    ]

    message = {
        'from_email': 'events@dancedeets.com',
        'from_name': 'DanceDeets Events',
        'subject': subject,
        'to': [{
            'email': email_address,
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
        logging.info('Sending new-user email for user %s (%s)', user.fb_uid, user.full_name)
        # And send the message now.
        mandrill_api.send_message(message)
    return message
