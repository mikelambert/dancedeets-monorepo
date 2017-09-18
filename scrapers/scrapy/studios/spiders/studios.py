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
    def __init__(self, allowed_domains):
        super(SameBaseDomainLinkExtractor, self).__init__()
        self.allowed_domains = allowed_domains

    def _extract_links(self, selector, response_url, response_encoding, base_url):
        links = super(SameBaseDomainLinkExtractor, self)._extract_links(selector, response_url, response_encoding, base_url)
        for link in links:
            if '/mindbody/' in link.url:
                continue
            parsed_link_url = urlparse(link.url)
            if parsed_link_url.netloc.lower() in self.allowed_domains:
                yield link


class AllStudiosScraper(spiders.CrawlSpider):
    name = 'AllStudios'
    allowed_domains = set()
    handle_httpstatus_list = [403]

    custom_settings = {
        'ITEM_PIPELINES': {
        }
    }

    def parse_start_url(self, response):
        # Allow start_urls to redirect somewhere else, and include that redirected domain
        parsed_url = urlparse(response.url)
        self.allowed_domains.add(parsed_url.netloc.lower())
        return []


    def parse_subpage(self, response):
        print response.url
        return None
        #parsed_url = urlparse(response.request.url)

    def __init__(self, *args, **kwargs):
        self.rules = (
            spiders.Rule(SameBaseDomainLinkExtractor(allowed_domains=self.allowed_domains), callback=self.parse_subpage, follow=True),
        )
        # We must set up self.rules before calling super, since super calls _compile_rules().
        super(AllStudiosScraper, self).__init__(*args, **kwargs)

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

                    parsed_url = urlparse(website)
                    self.allowed_domains.add(parsed_url.netloc.lower())
                    request = scrapy.Request(website, self.parse)
                    request.allow_redirect = True
                    yield request
                    return

