import yelp
import bing

class Yelp(object):
    def __init__(self):
        self.bearer_token = yelp.obtain_bearer_token(yelp.API_HOST, yelp.TOKEN_PATH)


    def _fetch_offset(self, city, offset, limit):
        url_params = {
            'location': city.replace(' ', '+'),
            'limit': limit,
            'categories': 'dance_schools,dancestudio',
            'offset': offset,
        }
        response = yelp.request(yelp.API_HOST, yelp.SEARCH_PATH, self.bearer_token, url_params=url_params)
        total = response['total']
        return total, response.get('businesses')

    def fetch_all(self, city):
        all_businesses = []
        batch = 50
        i = 0
        while True:
            total, businesses = self._fetch_offset(city, i * batch, batch)
            all_businesses.extend(businesses)
            print i * batch + batch, total
            if i * batch + batch > total:
                break
            i += 1
        return businesses

businesses = Yelp().fetch_all('New York, NY')

for x in businesses:
    print x['location']
    query = '%s %s' % (x['name'], ' '.join(x['display_address']))
    result = bing.bing_lucky(query)
    print query, result