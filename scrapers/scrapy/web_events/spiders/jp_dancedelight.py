# -*-*- encoding: utf-8 -*-*-

import datetime
import re
import urlparse

import scrapy

from dancedeets.events import namespaces
from dancedeets.loc import japanese_addresses
from .. import items
from .. import jp_spider


class DanceDelightScraper(items.WebEventScraper):
    name = 'DanceDelight'
    allowed_domains = ['www.dancedelight.net']
    namespace = namespaces.JAPAN_DD

    def start_requests(self):
        yield scrapy.Request('https://www.dancedelight.net/event/?pg=0')

    def parse(self, response):
        if '?pg=' in response.url:
            return self.parseList(response)
        else:
            return self.parseEvent(response)

    def parseList(self, response):
        next_url = response.xpath('//dd/a/@href').extract()
        for url in next_url:
            if '/event/' in url:
                yield scrapy.Request(urlparse.urljoin(response.url, url))

        event_urls = response.css('table.topics_list').xpath('.//a/@href').extract()
        for url in event_urls:
            yield scrapy.Request(urlparse.urljoin(response.url, url))

    def parseDateTimes(self, content_date):
        if ' ' in content_date:
            date_string, times_string = content_date.split(' ', 1)
        else:
            date_string = content_date
            times_string = ''
        date = datetime.datetime.strptime(date_string.strip(), '%Y/%m/%d').date()
        return jp_spider.parse_date_times(date, times_string.strip())

    def parseEvent(self, response):
        print response.url

        item = items.WebEvent()
        item['country'] = 'JP'
        item['namespace'] = self.namespace
        item['namespaced_id'] = re.search(r'/event/(\d+)', response.url).group(1)
        item['name'] = items.extract_text(response.css('div.title h2').xpath('.//text()'))

        photos = response.css('a.cb_photo').xpath('./@href').extract()
        if photos:
            item['photo'] = self.abs_url(response, photos[0])
        else:
            item['photo'] = None

        item['description'] = items.extract_text(response.css('div.tag_preview'))

        jp_addresses = japanese_addresses.find_addresses(item['description'])
        venue = jp_spider.get_venue_from_description(item['description'])
        jp_spider.setup_location(venue, jp_addresses, item)

        content_date = response.css('tr.event_date td').xpath('./text()').extract()[0]
        item['start_time'], item['end_time'] = self.parseDateTimes(content_date.strip())

        yield item
