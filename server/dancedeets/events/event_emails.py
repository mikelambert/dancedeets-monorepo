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
    in_event_emails = get_emails_from_string(event.description)
    emails.update(in_event_emails)
    for admin in event.admins:
        source = thing_db.Source.get_by_key_name(admin['id'])
        if not source or not source.emails:
            continue
        emails.update(source.emails)
    return emails
