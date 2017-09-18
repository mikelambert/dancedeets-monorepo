import sys
sys.path += ['lib/']
sys.path += ['../../server/']
sys.path += ['../../server/lib-local']
sys.path += ['../../server/lib-both']

import yelp
import bing

businesses = yelp.Yelp().fetch_all('New York, NY')

def get_page(business):
    pass
    #print business

def get_facebook(business):
    query = 'site:www.facebook.com %s %s' % (business['name'], business['location']['city'])
    print query
    results = bing.query(query)
    return results

for x in businesses:
    print x['name'], x['location']['display_address']
    get_page(x)
    #results =  get_facebook(x)
    #for x in results:
    #    print '  ', ' '.join(x)
