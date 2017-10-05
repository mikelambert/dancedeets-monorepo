import logging
import re

from google.appengine.ext import ndb

from dancedeets.event_scraper import thing_db
from dancedeets.events import eventdata
from dancedeets.server import api
from dancedeets import render_server


class NoEmailException(Exception):
    pass


class OrganizerEmailUnsubscribed(ndb.Model):
    @property
    def email(self):
        return str(self.key.string_id())


email_regex = re.compile((
    "([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
    "{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\."
    ")+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"
))


def filter_for_subscribed_emails(emails):
    unsubscribes_found = OrganizerEmailUnsubscribed.get_by_key_name(emails)
    return [email for unsubscribed, email in zip(unsubscribes_found, emails) if not unsubscribed]


def get_emails_from_string(s):
    """Returns an iterator of matched emails found in string s."""
    # Removing lines that start with '//' because the regular expression
    # mistakenly matches patterns like 'http://foo@bar.com' as '//foo@bar.com'.
    return [email for email in re.findall(email_regex, s) if not email[0].startswith('//')]


def get_emails_for_event(event):
    emails = set()
    event_emails = get_emails_from_string(event.description)
    emails.update(event_emails)
    for admin in event.admins:
        source = thing_db.Source.get_by_key_name(admin['id'])
        if not source or not source.emails:
            continue
        emails.update(source.emails)
    return emails


def send_event_add_emails(event_id):
    event = eventdata.DBEvent.get_by_id(event_id)
    emails = get_emails_for_event(event)
    for address in emails:
        try:
            email_contents = email_for_event(address, event, should_send=False)
            logging.info('Sent email: %s', email_contents)
        except NoEmailException as e:
            logging.info("Not sending email for event %s to address %s: %s", event.id, address, e)
            continue
        except Exception:
            logging.exception("Not sending email for event %s to address %s", event.id, address)
            continue


from dancedeets.mail import mandrill_api


def email_for_event(email, event, should_send=False):
    locale = 'en_US'
    api_event = api.canonicalize_event_data(event, None, None, (2, 0))
    props = {
        'currentLocale': locale.replace('_', '-'),
        'event': api_event,
    }
    response = render_server.render_jsx('eventAddMail.js', props, static_html=True)
    if response.error:
        message = 'Error rendering weeklyMail.js: %s' % response.error
        logging.error(message)
        raise NoEmailException(message)
    mjml_response = render_server.render_mjml(response.markup)
    rendered_html = mjml_response['html']

    message = {
        'from_email': 'events@dancedeets.com',
        'from_name': 'DanceDeets Events',
        'subject': 'Event Added',  # TODO
        'to': [{
            'email': email,
            'type': 'to',
        }],
        'html': rendered_html,
        'metadata': {
            'event_id': event.id,
            'email_type': 'add-event',
        },
        'tags': 'add-event',
    }
    if should_send:
        # And send the message now.
        mandrill_api.send_message(message)
    return message
