import base64
import hashlib
import hmac
import json
import logging
import urllib

import keys

USE_PRIVATE_KEY = True

google_maps_private_key = keys.get("google_maps_private_key")
google_server_key = keys.get("google_server_key")

def fetch_raw(address=None, latlng=None, language=None, region=None, components=None):
    params = {}
    if address is not None:
        params['address'] = address.encode('utf-8')
    if latlng is not None:
        params['latlng'] = '%s,%s' % latlng
    assert params
    params['sensor'] = 'false'
    if language is not None:
        params['language'] = language
    if region is not None:
        params['region'] = region
    if components is not None:
        params['components'] = components

    if USE_PRIVATE_KEY:
        params['client'] = 'free-dancedeets'
        unsigned_url_path = "/maps/api/geocode/json?%s" % urllib.urlencode(params)
        private_key = google_maps_private_key
        decoded_key = base64.urlsafe_b64decode(private_key)
        signature = hmac.new(decoded_key, unsigned_url_path, hashlib.sha1)
        encoded_signature = base64.urlsafe_b64encode(signature.digest())
        url = "https://maps.google.com%s&signature=%s" % (unsigned_url_path, encoded_signature)
    else:
        unsigned_url_path = "/maps/api/geocode/json?%s" % urllib.urlencode(params)
        url = "https://maps.google.com%s&key=%s" % (unsigned_url_path, google_server_key)

    logging.info('geocoding url: %s', url)
    result = urllib.urlopen(url).read()
    logging.info('geocoding results: %s', result)

    return json.loads(result)

