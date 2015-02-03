import os.path

import gmaps

def fetch_raw_cached(address=None, latlng=None, language='en'):

    if address is not None:
        filename = os.path.join('test_data/gmaps/address', language, address)
    elif latlng is not None:
        filename = os.path.join('test_data/gmaps/latlng', language, latlng)

    if os.path.exists(filename):
        return open(filename).read()
    else:
        result = gmaps.fetch_raw(address=address, latlng=latlng, language=language)
        open(filename, 'w').write(result)

    return result
