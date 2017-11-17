import logging
import re

from google.appengine.ext import ndb

from dancedeets.event_scraper import thing_db
from dancedeets.events import eventdata


class NoEmailException(Exception):
    pass


class OrganizerEmailUnsubscribed(ndb.Model):
    @property
    def email(self):
        return str(self.key.string_id())

    # When did they unsubscribe?
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    data = ndb.JsonProperty()


email_regex = re.compile((
    "([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
    "{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\."
    ")+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"
))


def filter_for_subscribed_emails(emails):
    unsubscribes_found = OrganizerEmailUnsubscribed.get_by_key_name(emails)
    return [email for unsubscribed, email in zip(unsubscribes_found, emails) if not unsubscribed]


def unsubscribe_email(email):
    o = OrganizerEmailUnsubscribed(key=email)
    o.put()


def get_emails_from_string(s):
    """Returns an iterator of matched emails found in string s."""
    # Removing lines that start with '//' because the regular expression
    # mistakenly matches patterns like 'http://foo@bar.com' as '//foo@bar.com'.
    return [email for email in re.findall(email_regex, s) if not email[0].startswith('//')]


def get_emails_for_event(event):
    emails = {}

    for email in get_emails_from_string(event.description):
        # Allow these names to be overridden later
        emails[email] = None

    for admin in event.admins:
        source = thing_db.Source.get_by_key_name(admin['id'])
        if not source or not source.emails:
            continue
        for email in source.emails:
            emails[email] = source.name

    if len(emails) > 1:
        logging.warning('Event %s (%s) has 2+ emails: %s', event.id, event.name, emails.items())
    return [{'email': email, 'name': name} for (email, name) in emails.items()]
