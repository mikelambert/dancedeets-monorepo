import logging
import re
import urlparse
from six.moves.urllib.parse import urlparse

import scrapy
from scrapy import item
from scrapy import spiders
from scrapy.linkextractors import LinkExtractor
from dancedeets.nlp import event_classifier
from dancedeets.nlp import regex_keywords
from dancedeets.nlp import keywords
from dancedeets.nlp import rules

from .. import yelp
from .. import facebook
"""
In start_requests:
- pass a city to the scraper
- grab all studios
- grab fb pages (use parse response api?)
Then, for each FB studio page:
- Send the FB page's website through the pipeline, as well as the linked-pages

TODO: If we can derive the class types from the FB info, use it
TODO: Prioritize the 'classes' page or 'about' page, to find keywords?
TODO: Check that they have a minimum number of styles, to be qualified as a "dance event styles" page (to avoid accidental matches)
TODO: Improve our keyword classifier, to be just the direct dance style names (not the 'related' ones)
TODO: Any other semantic pages we want to save? Schedule pages? Or Teachers pages?
"""


class SameBaseDomainLinkExtractor(LinkExtractor):
    def __init__(self, allowed_domains):
        super(SameBaseDomainLinkExtractor, self).__init__()
        self.allowed_domains = allowed_domains

    def _extract_links(self, selector, response_url, response_encoding, base_url):
        links = super(SameBaseDomainLinkExtractor, self)._extract_links(selector, response_url, response_encoding, base_url)
        for link in links:
            if '/mindbody/' in link.url:
                continue
            # Wordpress/Blog sites
            if '/tag/' in link.url:
                continue
            if '/category/' in link.url:
                continue
            if '/author' in link.url:
                continue
            if '/blog/' in link.url:
                continue
            if 'replytocom=' in link.url:
                continue
            if 'author=1' in link.url:
                continue
            parsed_link_url = urlparse(link.url)
            if parsed_link_url.netloc.lower() in self.allowed_domains:
                yield link


class AllStudiosScraper(spiders.CrawlSpider):
    name = 'AllStudios'
    allowed_domains = set()
    handle_httpstatus_list = [403]

    custom_settings = {
        'ITEM_PIPELINES': {},
        'HTTPCACHE_ENABLED': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        #'DOWNLOAD_DELAY': 5,
        'DEPTH_LIMIT': 1,  # why doesn't this work?
        'DEPTH_PRIORITY': 1,
    }

    def __init__(self, *args, **kwargs):
        self.rules = (
            spiders.Rule(SameBaseDomainLinkExtractor(allowed_domains=self.allowed_domains), callback=self._parse_contents, follow=True),
        )
        logging.getLogger('scrapy.core.engine').setLevel(logging.INFO)
        logging.getLogger('scrapy.downloadermiddlewares.redirect').setLevel(logging.INFO)
        logging.getLogger('scrapy.spidermiddlewares.depth').setLevel(logging.INFO)

        # We must set up self.rules before calling super, since super calls _compile_rules().
        super(AllStudiosScraper, self).__init__(*args, **kwargs)

    def parse_start_url(self, response):
        # Allow start_urls to redirect somewhere else, and include that redirected domain
        parsed_url = urlparse(response.url)
        self.allowed_domains.add(parsed_url.netloc.lower())
        self._parse_contents(response)
        return []

    def _parse_contents(self, response):
        if not hasattr(response, 'selector'):
            logging.info('Skipping unknown file from: %s', response.url)
            return
        # Get all text contents of tags (unless they are script or style tags)
        text_contents = ' '.join(response.selector.xpath('//*[not(self::script|self::style)]/text()').extract()).lower()

        processed_text = event_classifier.StringProcessor(text_contents, regex_keywords.WORD_BOUNDARIES)
        wrong = processed_text.get_tokens(keywords.DANCE_WRONG_STYLE)
        good = processed_text.get_tokens(rules.STREET_STYLE)
        if (wrong or good):
            print response.url, set(wrong), set(good)

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
                    websites = result['website']
                    for website in websites.strip().split(' '):
                        if not website.startswith('http'):
                            website = 'http://%s' % website
                        if 'twitter.com' in website or 'yelp.com' in website or 'facebook.com' in website or 'youtube.com' in website or 'vimeo.com' in website:
                            continue

                        parsed_url = urlparse(website)
                        self.allowed_domains.add(parsed_url.netloc.lower())
                        request = scrapy.Request(website, self.parse)
                        request.allow_redirect = True
                        yield request
