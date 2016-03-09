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


def google_api_json_request(protocol_host, path, params, use_private_key):
    params = params.copy()
    if use_private_key:
        params['client'] = 'free-dancedeets'
        unsigned_url_path = "%s?%s" % (path, urllib.urlencode(params))
        private_key = google_maps_private_key
        decoded_key = base64.urlsafe_b64decode(private_key)
        signature = hmac.new(decoded_key, unsigned_url_path, hashlib.sha1)
        encoded_signature = base64.urlsafe_b64encode(signature.digest())
        url = "%s%s&signature=%s" % (protocol_host, unsigned_url_path, encoded_signature)
    else:
        unsigned_url_path = "%s?%s" % (path, urllib.urlencode(params))
        url = "%s%s&key=%s" % (protocol_host, unsigned_url_path, google_server_key)

    logging.info('geocoding url: %s', url)
    result = urllib.urlopen(url).read()
    logging.info('geocoding results: %s', result)

    return json.loads(result)


def fetch_raw(address=None, latlng=None, language=None, region=None, components=None):
    params = {}
    if address is not None:
        params['address'] = address.encode('utf-8')
    if latlng is not None:
        params['latlng'] = '%s,%s' % latlng
    assert params
    if language is not None:
        params['language'] = language
    if region is not None:
        params['region'] = region
    if components is not None:
        params['components'] = components

    return google_api_json_request('https://maps.google.com', '/maps/api/geocode/json', params, use_private_key=USE_PRIVATE_KEY)


def fetch_places_raw(query=None, language=None):
    params = {}
    params['query'] = query.encode('utf-8')
    if language is not None:
        params['language'] = language

    return google_api_json_request('https://maps.googleapis.com', '/maps/api/place/textsearch/json', params, use_private_key=False)
