import urllib
import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor

from .. import items


def split_list_on_element(lst, split_elem):
    new_list = ['']
    for elem in lst:
        if split_elem(elem):
            new_list.append('')
        else:
            new_list[-1] += elem
    return [x.strip() for x in new_list]


class ComeOn5678Scraper(items.WebEventScraper):
    name = 'ComeOn5678'
    allowed_domains = ['comeon5678.com']

    def start_requests(self):
        yield scrapy.Request('http://comeon5678.com/event/list?p=1')

    def parse(self, response):
        e = LinkExtractor()
        urls = [link.url for link in e.extract_links(response)]
        for url in urls:
            yield items.AddFacebookEvent(url)
        if urls:
            qs = urlparse.parse_qs(urlparse.urlparse(response.url).query)
            qs = dict((k, v[0]) for (k, v) in qs.iteritems())
            qs['p'] = int(qs['p']) + 1
            url = 'http://comeon5678.com/event/list'
            yield scrapy.Request('%s?%s' % (url, urllib.urlencode(qs)))
