import base64
import hashlib
import hmac
import json
import logging
import urllib

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

