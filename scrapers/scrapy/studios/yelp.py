import json
import os
import yelp_core

try:
    os.makedirs('yelp_cache')
except OSError:
    pass

class Yelp(object):
    def __init__(self):
        self.bearer_token = yelp_core.obtain_bearer_token(yelp_core.API_HOST, yelp_core.TOKEN_PATH)


    def _fetch_offset(self, city, offset, limit):
        url_params = {
            'location': city.replace(' ', '+'),
            'limit': limit,
            'categories': 'dance_schools,dancestudio',
            'offset': offset,
        }
        response = yelp_core.request(yelp_core.API_HOST, yelp_core.SEARCH_PATH, self.bearer_token, url_params=url_params)
        total = response['total']
        return total, response.get('businesses')

    def _cache_name(self, city):
        return 'yelp_cache/%s.txt' % city.lower().replace(' ', '-').replace(',', '')

    def _get_cache(self, city):
        try:
            return json.loads(open(self._cache_name(city)).read())
        except IOError:
            return None

    def _set_cache(self, city, data):
        return open(self._cache_name(city), 'w').write(json.dumps(data))

    def fetch_all(self, city):
        cached_result = self._get_cache(city)
        if cached_result is not None:
            return cached_result

        all_businesses = []
        batch = 50
        i = 0
        while True:
            total, businesses = self._fetch_offset(city, i * batch, batch)
            all_businesses.extend(businesses)
            if i * batch + batch > total:
                break
            i += 1

        self._set_cache(city, all_businesses)
        return all_businesses
