import sys
sys.path += ['lib/']
sys.path += ['../../server/']
sys.path += ['../../server/lib-local']
sys.path += ['../../server/lib-both']

import yelp
import bing
import facebook

businesses = (
    yelp.Yelp().fetch_all('San Francisco, CA') +
    yelp.Yelp().fetch_all('Los Angeles, CA') +
    yelp.Yelp().fetch_all('New York, NY') +
    []
)

fb_place_fields = 'id,about,category,category_list,company_overview,contact_address,cover,current_location,description,emails,fan_count,general_info,is_permanently_closed,location,link,name,phone,website,was_here_count'

show_good = True

for x in businesses:
    args = dict(type='place', q=x['name'], limit=1, fields=fb_place_fields)
    if x['coordinates']['latitude']:
        args['center'] = '%s,%s' % (x['coordinates']['latitude'], x['coordinates']['longitude'])
    results = facebook.search(**args)
    if 'data' not in results:
        raise Exception('Error on %s: %s' % (x['name'], results))
    if results['data']:
        result = results['data'][0]
        if 'website' in result:
            if show_good:
                print x['name'].encode('utf-8'), result['link'], result['website']
        else:
            if not show_good:
                print x['name'].encode('utf-8')
                print '  ', result['link']
    else:
        if not show_good:
            print x['name'].encode('utf-8')
            print '  Not found!'
    #print ''