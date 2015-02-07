import base64
import hashlib
import hmac
import json
import logging
import urllib

class GeocodeException(Exception):
    pass

def fetch_raw(address=None, latlng=None, language=None, region=None):
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
    if region is not None:
        params['region'] = region
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

    return json.loads(result)

class GMapsGeocode(object):
    def __init__(self, json_data):
        self.json_data = json_data

    def copy(self):
        return GMapsGeocode(self.json_data)

    def address_components(self):
        return self.json_data['address_components']

    def get_component(self, name, long=True):
        components = [x[long and 'long_name' or 'short_name'] for x in self.json_data['address_components'] if name in x['types']]
        if components:
            return components[0]
        else:
            return None

    def delete_component(self, name):
        self.json_data['address_components'] = [x for x in self.json_data['address_components'] if name not in x['types']]

def parse_geocode(json_result):
    if json_result['status'] == 'OK':
        return GMapsGeocode(json_result['results'][0])
    elif json_result['status'] == 'ZERO_RESULTS':
        return None
    else:
        raise GeocodeException("Got unexpected status: %s" % json_result['status'])
