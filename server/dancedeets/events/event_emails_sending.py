# -*-*- encoding: utf-8 -*-*-

import datetime
from icemac.truncatetext import truncate
import logging
import urllib

from dancedeets import render_server
from dancedeets.events import eventdata
from dancedeets.events import event_emails
from dancedeets.logic import api_format
from dancedeets.logic import mobile
from dancedeets.mail import mandrill_api


class NoEmailException(Exception):
    pass


def send_event_add_emails(event_id, should_send=False):
    event = eventdata.DBEvent.get_by_id(event_id)
    if (event.end_time or event.start_time) < datetime.datetime.now():
        logging.info('Not sending event email because event is in the past.')
        return []
    # We could also send a single email to all the organizers. Problems with this include:
    # - It becomes a little more confusing to see what to call the "Dear X"
    # - It's harder to pre-fill an unsubscribe-email-address
    emails = event_emails.get_emails_for_event(event)
    email_contents = []
    for organizer in emails:
        try:
            email_contents.append(email_for_event(organizer, event, should_send=should_send))
            logging.info('Sent email: %s', email_contents)
        except NoEmailException as e:
            logging.info("Not sending email for event %s to address %s: %s", event.id, organizer, e)
            continue
        except Exception:
            logging.exception("Not sending email for event %s to address %s", event.id, organizer)
            continue
    return email_contents


def email_for_event(organizer, event, should_send=False):
    locale = 'en_US'
    api_event = api_format.canonicalize_event_data(event, (2, 0))
    email_address = organizer['email']
    email_unsubscribe_url = 'https://www.dancedeets.com/user/unsubscribe?email=%s' % urllib.quote(email_address)
    props = {
        'event': api_event,
        'organizer': organizer,
        'currentLocale': locale.replace('_', '-'),
        'mobileIosUrl': mobile.IOS_URL,
        'mobileAndroidUrl': mobile.ANDROID_URL,
        'emailPreferencesUrl': email_unsubscribe_url,
    }
    response = render_server.render_jsx('mailAddEvent.js', props, static_html=True)
    if response.error:
        message = 'Error rendering mailAddEvent.js: %s' % response.error
        logging.error(message)
        raise NoEmailException(message)
    mjml_response = render_server.render_mjml(response.markup)
    if mjml_response.get('errors'):
        message = 'Errors rendering mailAddEvent.mjml: %s', mjml_response['errors']
        logging.error(message)
        raise NoEmailException(message)
    rendered_html = mjml_response['html']

    short_name = truncate(event.name, 30, ellipsis=u'…')
    message = {
        'from_email': 'events@dancedeets.com',
        'from_name': 'DanceDeets Events',
        'subject': 'Your event "%s" has been added to DanceDeets!' % short_name,
        'to': [{
            'email': email_address,
            'type': 'to',
        }],
        'bcc_address': 'mlambert@dancedeets.com',
        'html': rendered_html,
        'metadata': {
            'event_id': event.id,
            'email_type': 'add-event',
        },
        'tags': ['add-event'],
    }
    if should_send:
        # And send the message now.
        mandrill_api.send_message(message)
    return message
