import gcm
import keys

def android_notify(user, title, text, url):
    g = gcm.GCM(keys.get('google_server_key'), debug=True)
    tokens = user.json_data['android_device_token']
    data = {
        'title': title,
        'text': text,
        'url': url,
    }
    return g.json_request(registration_ids=tokens, data=data)
