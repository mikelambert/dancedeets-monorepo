import sys
sys.path += ['lib/']
sys.path += ['../../server/']
sys.path += ['../../server/lib-local']
sys.path += ['../../server/lib-both']

import yelp
import bing
import facebook

businesses = yelp.Yelp().fetch_all('New York, NY')

fb_place_fields = 'id,about,category,category_list,company_overview,contact_address,cover,current_location,description,emails,fan_count,general_info,is_permanently_closed,location,link,name,phone,website,was_here_count'

for x in businesses:
    print x['name']
    # use x['location']['city']
    results = facebook.search(type='place', q=x['name'], limit=1, fields=fb_place_fields)
    result = results['data'][0]
    print result['name']
