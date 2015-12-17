import logging

import gcm

import keys
from util import urls

def notify(user, event, title, text):
    # TODO: We don't want to send raw URLs, or it pops open a "open with" dialog. Pass in a custom schema instead!
    url = urls.fb_event_url(event.fb_event_id)

    g = gcm.GCM(keys.get('google_server_key'), debug=True)
    tokens = user.device_tokens('android')
    duration = 60*70 # 70 minutes
    # or maybe better, end-datetime.datetime.now()?
    data = {
        'title': title,
        'text': text,
        'url': url,
        'delay_while_idle': 0,
        'time_to_live': duration,
    }
    # TODO: what happens if we send multiple notifications. last-one wins? Can we do a better job of prioritizing and aggregating these?
    response = g.json_request(registration_ids=tokens, data=data)

    changed_tokens = False
    if 'errors' in response:
        for error, reg_ids in response['errors'].iteritems():
            if error in ('NotRegistered', 'InvalidRegistration'):
                for reg_id in reg_ids:
                    tokens.remove(reg_id)
                    changed_tokens = True
            else:
                logging.error("Error for user %s with url %s: %s", user.fb_uid, url, error)

    if 'canonical' in response:
        for reg_id, canonical_id in response['canonical'].iteritems():
            tokens.remove(reg_id)
            tokens.append(canonical_id)
            changed_tokens = True

    if changed_tokens:
        user.put()

    return 'success' in response

