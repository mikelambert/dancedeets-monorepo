# -*-*- encoding: utf-8 -*-*-

import datetime
import re
import urlparse

import scrapy

from events import namespaces
from loc import japanese_addresses
from .. import items
from .. import jp_spider
from util import strip_markdown


class DanceDelightScraper(items.WebEventScraper):
    name = 'DanceDelight'
    allowed_domains = ['www.dancedelight.net']
    namespace = namespaces.JAPAN_DD

    def start_requests(self):
        yield scrapy.Request('http://www.dancedelight.net/wordpress/?cat=6')

    def parse(self, response):
        if '?cat=' in response.url:
            return self.parseList(response)
        else:
            return self.parseEvent(response)

    def parseList(self, response):
        next_url = response.xpath('//a[@rel="next"]/@href').extract()
        for url in next_url:
            yield scrapy.Request(urlparse.urljoin(response.url, url))

        event_urls = response.xpath('//a[@rel="bookmark"]/@href').extract()
        for url in event_urls:
            yield scrapy.Request(urlparse.urljoin(response.url, url))

    def parseDateTimes(self, content_date, post_text):
        month_date_re = ur'(\d+)月\s*(\d+)'
        date_match = re.search(month_date_re, content_date)
        month, day = jp_spider._intall(date_match.groups())
        start_date = datetime.date.today().replace(month=month, day=day)
        if datetime.date.today() - datetime.timedelta(days=7) > start_date:
            start_date = start_date.replace(year=start_date.year + 1)
        return jp_spider.parse_date_times(start_date, post_text)

    def parseEvent(self, response):
        print response.url

        item = items.WebEvent()
        item['namespace'] = self.namespace
        item['namespaced_id'] = re.search(r'\?p=(\d+)', response.url).group(1)
        item['name'] = self._extract_text(response.xpath('//a[@rel="bookmark"]/text()'))

        post = response.css('.entry-content')

        photos = post.css('img.size-full').xpath('./@src').extract()
        if photos:
            item['photo'] = photos[0]
        else:
            item['photo'] = None

        post_html = post.extract()[0]
        post_top = response.css('.social4i').extract()[0]
        post_html = post_html.replace(post_top, '')

        full_description = items._format_text(post_html)
        item['description'] = strip_markdown.strip(full_description)

        jp_addresses = japanese_addresses.find_addresses(item['description'])
        venue = items.get_line_after(item['description'], ur'場所|会場')
        jp_spider.setup_location(venue, jp_addresses, item)

        content_date = ''.join(response.css('.contentdate').xpath('.//text()').extract())
        item['start_time'], item['end_time'] = self.parseDateTimes(content_date, full_description)

        #item['latitude'] = latlng['lat']
        #item['longitude'] = latlng['lng']

        yield item
