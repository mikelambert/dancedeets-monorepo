import json
import urllib

import keys
from . import gmaps_backends

class ProdServerBackend(gmaps_backends.GMapsBackend):
    def __init__(self, lookup_type, backend):
        self.lookup_type = lookup_type
        self.backend = backend

    def get_json(self, **kwargs):
        post_data = json.dumps({
            'private_key': keys.get('private_key'),
            'lookup_type': self.lookup_type,
            'lookup': kwargs,
        })
        url = 'http://www.dancedeets.com/_gmaps_api'
        file = urllib.urlopen(url, post_data)
        try:
            response = file.read()
        finally:
            file.close()
        if file.getcode() == 200:
            return json.loads(response)
        else:
            return self.backend.get_json(**kwargs)

    def delete(self, **kwargs):
        # noop
        self.backend.delete(**kwargs)
