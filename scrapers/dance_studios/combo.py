import sys
sys.path += ['lib/']
sys.path += ['../../server/']
sys.path += ['../../server/lib-local']
sys.path += ['../../server/lib-both']

import yelp
from py_ms_cognitive import PyMsCognitiveWebSearch
from dancedeets import keys

businesses = yelp.Yelp().fetch_all('New York, NY')

def bing(query):
    search_service = PyMsCognitiveWebSearch(keys.get('bing_api_key'), query)
    first_fifty_result = search_service.search(limit=10, format='json') #1-50
    return [(x.name, x.display_url) for x in first_fifty_result]

def get_page(business):
    pass
    #print business

def get_facebook(business):
    query = 'site:www.facebook.com %s %s' % (business['name'], business['location']['city'])
    print query
    results = bing(query)
    return results

for x in businesses:
    print x['name'], x['location']['display_address']
    get_page(x)
    #results =  get_facebook(x)
    #for x in results:
    #    print '  ', ' '.join(x)
