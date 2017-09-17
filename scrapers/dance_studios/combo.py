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
            if i * batch + batch > total:
                break
            i += 1
            break # TODO: remove
        return businesses

businesses = Yelp().fetch_all('New York, NY')

for x in businesses:
    query = 'site:www.facebook.com %s %s' % (x['name'], ' '.join(x['location']['display_address']))
    results = bing.bing_lucky(query)
    print query
    for x in results:
        print '  ', ' '.join(x)
