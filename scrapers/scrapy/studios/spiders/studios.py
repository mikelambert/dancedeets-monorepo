import re
import urlparse
from six.moves.urllib.parse import urlparse

import scrapy
from scrapy import item
from scrapy import spiders
from scrapy.linkextractors import LinkExtractor

from .. import yelp
from .. import facebook

class SameBaseDomainLinkExtractor(LinkExtractor):
    def _extract_links(self, selector, response_url, response_encoding, base_url):
        links = super(SameBaseDomainLinkExtractor, self)._extract_links(selector, response_url, response_encoding, base_url)
        parsed_base_url = urlparse(base_url)
        for link in links:
            parsed_link_url = urlparse(link.url)
            if parsed_base_url.netloc.lower() == parsed_link_url.netloc.lower():
                yield link


class AllStudiosScraper(spiders.CrawlSpider):
    name = 'AllStudios'
    allowed_domains = []
    handle_httpstatus_list = [403]

    custom_settings = {
        'ITEM_PIPELINES': {
        }
    }

    rules = (
        spiders.Rule(SameBaseDomainLinkExtractor()),
    )


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
                    return

