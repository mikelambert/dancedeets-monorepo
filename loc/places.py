import base64
import hashlib
import hmac
import json
import logging
import urllib

import keys

USE_PRIVATE_KEY = False

google_maps_private_key = keys.get("google_maps_private_key")
google_server_key = keys.get("google_server_key")


def fetch_raw(query=None, language=None):
    params = {}
    params['query'] = query.encode('utf-8')
    if language is not None:
        params['language'] = language

    if USE_PRIVATE_KEY:
        params['client'] = 'free-dancedeets'
        unsigned_url_path = "/maps/api/place/textsearch/json?%s" % urllib.urlencode(params)
        private_key = google_maps_private_key
        decoded_key = base64.urlsafe_b64decode(private_key)
        signature = hmac.new(decoded_key, unsigned_url_path, hashlib.sha1)
        encoded_signature = base64.urlsafe_b64encode(signature.digest())
        url = "https://maps.googleapis.com%s&signature=%s" % (unsigned_url_path, encoded_signature)
    else:
        unsigned_url_path = "/maps/api/place/textsearch/json?%s" % urllib.urlencode(params)
        url = "https://maps.googleapis.com%s&key=%s" % (unsigned_url_path, google_server_key)

    logging.info('placesearch url: %s', url)
    result = urllib.urlopen(url).read()
    logging.info('placesearch results: %s', result)

    return json.loads(result)

