import re
import urlparse

import scrapy
from scrapy import item

from .. import yelp
from .. import facebook

class AllStudiosScraper(scrapy.Spider):
    name = 'AllStudios'
    allowed_domains = []

    custom_settings = {
        'ITEM_PIPELINES': {
        }
    }

    def start_requests(self):
        self.businesses = yelp.Yelp().fetch_all(self.city)

        fb_place_fields = 'id,about,category,category_list,company_overview,contact_address,cover,current_location,description,emails,fan_count,general_info,is_permanently_closed,location,link,name,phone,website'
        for x in self.businesses:
            args = dict(type='place', q=x['name'], limit=1, fields=fb_place_fields)
            if x['coordinates']['latitude']:
                args['center'] = '%s,%s' % (x['coordinates']['latitude'], x['coordinates']['longitude'])
            results = facebook.search(**args)
            if results['data']:
                result = results['data'][0]
                if 'website' in result:
                    website = result['website']
                    if not website.startswith('http'):
                        website = 'http://%s' % website
                    yield scrapy.Request(website, self.parse)

    def parse(self, response):
        print response
