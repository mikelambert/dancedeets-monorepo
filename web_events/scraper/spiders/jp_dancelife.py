# -*-*- encoding: utf-8 -*-*-
import datetime
import re

import scrapy

from events import namespaces
from loc import japanese_addresses
from .. import items
from .. import jp_spider


class TokyoDanceLifeScraper(items.WebEventScraper):
    name = 'TokyoDanceLife'
    allowed_domains = ['www.tokyo-dancelife.com']
    namespace = namespaces.JAPAN_TDL

    def start_requests(self):
        yield scrapy.Request('http://www.tokyo-dancelife.com/event/')

    def parse(self, response):
        if response.url.endswith('/'):
            return self.parseList(response)
        else:
            return self.parseEvent(response)

    def parseList(self, response):
        PAST_EVENTS = False
        if PAST_EVENTS:
            monthly_page_urls = response.css('div#pastevent-area').xpath('.//a/@href').extract()
            for url in monthly_page_urls:
                yield scrapy.Request(self.abs_url(response, url))

        event_urls = response.xpath('//div[@class="name"]/a/@href').extract()
        for url in event_urls:
            yield scrapy.Request(self.abs_url(response, url))

    def parseDateTimes(self, response):
        day_text = items.extract_text(response.css('div.day'))
        month, day = re.search(r'(\d+)\.(\d+)', day_text).groups()
        year = re.search(r'/(\d\d\d\d)_\d+/', response.url).group(1)
        start_date = datetime.date(int(year), int(month), int(day))

        return jp_spider.parse_date_times(start_date, items.extract_text(response.xpath('//dl')))

    def parseEvent(self, response):
        print response.url

        item = items.WebEvent()
        item['namespace'] = self.namespace
        item['namespaced_id'] = re.search(r'/(\d+)\.php', response.url).group(1)
        item['name'] = items.extract_text(response.css('div.event-detail-name'))

        photos = response.css('div.event-detail-img').xpath('./a/@href').extract()
        if photos:
            item['photo'] = self.abs_url(response, photos[0])
        else:
            item['photo'] = None

        category = response.css('div.event-detail-koumoku').xpath('./img/@alt').extract()[0]
        # Because dt otherwise remains flush up against the end of the previous dd, we insert manual breaks.
        full_description = items.format_text(response.xpath('//dl').extract()[0].replace('<dt>', '<dt><br><br>'))
        item['description'] = '%s\n\n%s' % (category, full_description)

        jp_addresses = japanese_addresses.find_addresses(item['description'])
        venue = jp_spider.get_venue_from_description(item['description'])
        jp_spider.setup_location(venue, jp_addresses, item)

        item['start_time'], item['end_time'] = self.parseDateTimes(response)

        yield item
