import logging
from mailchimp3 import MailChimp
import md5
from requests import exceptions

import keys
from util import runtime

client = MailChimp(keys.get('mailchimp_username'), keys.get('mailchimp_key'))

LIST_WEB_ID = 554989
LIST_ID = '93ab23d636'

class UserNotFound(Exception):
    pass

def get_list_id():
    lists = client.lists.all()
    list_id = [x['id'] for x in lists['lists'] if x['web_id'] == LIST_WEB_ID][0]
    return list_id

def add_members(list_id, members):
    data = {
        'members': members,
        'update_existing': True,
    }
    if runtime.is_appengine():
        return client.lists.update_members(list_id=list_id, data=data)
    else:
        return {'errors': []}

def update_email(list_id, old_email, new_email):
    data = {
        'email_address': new_email,
    }
    subscriber_hash = md5.new(old_email.lower()).hexdigest()
    logging.info('Updating subscriber_hash %s (%s) to %s', subscriber_hash, old_email, new_email)
    if runtime.is_appengine():
        try:
            return client.lists.members.update(list_id=list_id, subscriber_hash=subscriber_hash, data=data)
        except exceptions.HTTPError:
            raise UserNotFound()
    else:
        return {'errors': []}
