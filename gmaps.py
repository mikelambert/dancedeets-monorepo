import base64
import hashlib
import hmac
import json
import logging
import urllib

class GeocodeException(Exception):
    pass

def fetch_raw(address=None, latlng=None, language=None):
    params = {}
    if address is not None:
        params['address'] = address.encode('utf-8')
    if latlng is not None:
        params['latlng'] = '%s,%s' % latlng
    assert params
    params['sensor'] = 'false'
    params['client'] = 'free-dancedeets'
    if language is not None:
        params['language'] = language
    unsigned_url_path = "/maps/api/geocode/json?%s" % urllib.urlencode(params)
    private_key = 'zj918QnslsoOQHl4kLjv-ZCgsDE='
    decoded_key = base64.urlsafe_b64decode(private_key)
    signature = hmac.new(decoded_key, unsigned_url_path, hashlib.sha1)
    encoded_signature = base64.urlsafe_b64encode(signature.digest())

    url = "http://maps.google.com%s&signature=%s" % (unsigned_url_path, encoded_signature)
    print url

    logging.info('geocoding url: %s', url)
    result = urllib.urlopen(url).read()
    logging.info('geocoding results: %s', result)
    return result

def fetch_json(address=None, latlng=None, fetch_raw=fetch_raw):
    results = fetch_raw(address=address, latlng=latlng)
    try:
        json_result = json.loads(results)
    except json.decoder.JSONDecodeError, e:
        raise GeocodeException("Error decoding json from %s: %s: %r" % (e, results))
    return json_result

def fetch_geocode(address=None, latlng=None):
    json_result = fetch_raw(address=address, latlng=latlng)
    if json_result['status'] == 'ZERO_RESULTS':
        return ''
    if json_result['status'] != 'OK':
        raise GeocodeException("Got unexpected status: %s" % json_result['status'])
    result = json_result['results'][0]
    return result

def debug_types(**kwargs):
    result = fetch_geocode(**kwargs)
    for c in result['address_components']:
        print c['long_name'], c['short_name'], c['types']
    print result['formatted_address']
    print result['types']
