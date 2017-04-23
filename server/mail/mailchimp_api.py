from mailchimp3 import MailChimp

import keys
from util import runtime

client = MailChimp(keys.get('mailchimp_username'), keys.get('mailchimp_key'))

LIST_WEB_ID = 554989

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
