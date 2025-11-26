import json
import logging
import requests

from dancedeets import keys
from . import gmaps_backends


class ProdServerBackend(gmaps_backends.GMapsBackend):
    def __init__(self, lookup_type, backend):
        self.lookup_type = lookup_type
        self.backend = backend

    def get_json(self, **kwargs):
        post_data = {
            'private_key': keys.get('private_readonly_key'),
            'lookup_type': self.lookup_type,
            'lookup': kwargs,
        }
        url = 'https://www.dancedeets.com/_gmaps_api'
        response = requests.post(url, json=post_data)
        if response.status_code == 200:
            logging.info('Returning result from prod server: %s', post_data)
            return response.json()
        else:
            return self.backend.get_json(**kwargs)

    def delete(self, **kwargs):
        # noop
        self.backend.delete(**kwargs)
