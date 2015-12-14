import logging

import gcm

import keys

def android_notify(user, title, text, url):
    g = gcm.GCM(keys.get('google_server_key'), debug=True)
    tokens = user.device_tokens('android')
    data = {
        'title': title,
        'text': text,
        'url': url,
    }
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

