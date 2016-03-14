import base64
import hashlib
import hmac
import json
import logging
import urllib

import keys

from . import gmaps_backends

google_maps_private_key = keys.get("google_maps_private_key")
google_server_key = keys.get("google_server_key")


class LiveBackend(gmaps_backends.GMapsBackend):
    def __init__(self, protocol_host, path, use_private_key):
        self.protocol_host = protocol_host
        self.path = path
        self.use_private_key = use_private_key

    def get_json(self, **kwargs):
        if self.use_private_key:
            kwargs['client'] = 'free-dancedeets'
            kwargs = dict((k.encode('utf-8'), v.encode('utf-8')) for k, v in kwargs.items())
            unsigned_url_path = "%s?%s" % (self.path, urllib.urlencode(kwargs))
            private_key = google_maps_private_key
            decoded_key = base64.urlsafe_b64decode(private_key)
            signature = hmac.new(decoded_key, unsigned_url_path, hashlib.sha1)
            encoded_signature = base64.urlsafe_b64encode(signature.digest())
            url = "%s%s&signature=%s" % (self.protocol_host, unsigned_url_path, encoded_signature)
        else:
            unsigned_url_path = "%s?%s" % (self.path, urllib.urlencode(kwargs))
            url = "%s%s&key=%s" % (self.protocol_host, unsigned_url_path, google_server_key)

        logging.info('geocoding url: %s', url)
        result = urllib.urlopen(url).read()
        logging.info('geocoding results: %s', result)

        return json.loads(result)
