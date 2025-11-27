import hashlib
import logging
from mailchimp3 import MailChimp
from requests import exceptions

from dancedeets import keys
from dancedeets.util import runtime

_client = None
LIST_WEB_ID = 554989
LIST_ID = '93ab23d636'


def get_client():
    """Lazy initialization of MailChimp client."""
    global _client
    if _client is None:
        # Note: In mailchimp3 2.1.0+, argument order is (api_key, username), not (username, api_key)
        api_key = keys.get('mailchimp_key')
        username = keys.get('mailchimp_username')
        _client = MailChimp(mc_api=api_key, mc_user=username) if api_key != keys.NO_KEY else None
    return _client


class UserNotFound(Exception):
    pass


def get_list_id():
    client = get_client()
    if not client:
        return LIST_ID
    lists = client.lists.all()
    list_id = [x['id'] for x in lists['lists'] if x['web_id'] == LIST_WEB_ID][0]
    return list_id


def add_members(list_id, members):
    data = {
        'members': members,
        'update_existing': True,
    }
    client = get_client()
    if runtime.is_appengine() and client:
        return client.lists.update_members(list_id=list_id, data=data)
    else:
        return {'errors': []}


def update_email(list_id, old_email, new_email):
    data = {
        'email_address': new_email,
    }
    subscriber_hash = hashlib.md5(old_email.lower().encode()).hexdigest()
    logging.info('Updating subscriber_hash %s (%s) to %s', subscriber_hash, old_email, new_email)
    client = get_client()
    if runtime.is_appengine() and client:
        try:
            return client.lists.members.update(list_id=list_id, subscriber_hash=subscriber_hash, data=data)
        except exceptions.HTTPError:
            raise UserNotFound()
    else:
        return {'errors': []}
