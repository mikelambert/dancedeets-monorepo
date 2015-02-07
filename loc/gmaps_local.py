import json
import os.path

import gmaps

def fetch_raw_cached(address=None, latlng=None, language='en'):

    if address is not None:
        filename = os.path.join('test_data/gmaps/address', language, address)
    elif latlng is not None:
        filename = os.path.join('test_data/gmaps/latlng', language, latlng)

    if not os.path.exists(filename):
        json_result = gmaps.fetch_raw(address=address, latlng=latlng, language=language)
        result = json.dumps(json_result)
        f = open(filename, 'w')
        f.write(result)
        f.close()

    result = open(filename).read()
    json_result = json.loads(result)
    return json_result
