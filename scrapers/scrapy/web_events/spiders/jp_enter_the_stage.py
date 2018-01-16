# -*-*- encoding: utf-8 -*-*-

import datetime
import logging
import re

import scrapy

from dancedeets.events import namespaces
from dancedeets.loc import japanese_addresses
from .. import items
from .. import jp_spider

time_re = ur'(\d+)[時:](\d+)[分]?'
date_time_re = ur'(\d+)[年.](\d+)[月.](\d+)[日.]? %s' % time_re


def _intall(lst):
    return [int(x) for x in lst]


def parse_times(s):
    # '2016年03月09日 23時30分～2016年03月10日 05時30分'
    # '2016年03月10日 20時00分～23時30分'
    start_str, end_str = s.split(u'～')
    start_match = re.match(date_time_re, start_str)
    if not start_match:
        raise ValueError("Could not parse start time: %s" % start_str)
    start_datetime = datetime.datetime(*jp_spider._intall(start_match.groups()))

    end_match = re.match(date_time_re, end_str)
    if end_match:
        end_datetime = datetime.datetime(*jp_spider._intall(end_match.groups()))
    else:
        end_match = re.match(time_re, end_str)
        if end_match:
            end_time = datetime.time(*jp_spider._intall(end_match.groups()))
            end_datetime = datetime.datetime.combine(start_datetime.date(), end_time)
        else:
            raise ValueError("Could not parse end time: %s" % end_str)
    return (start_datetime, end_datetime)


class EnterTheStageScraper(items.WebEventScraper):
    name = 'EnterTheStage'
    allowed_domains = ['et-stage.net']
    namespace = namespaces.JAPAN_ETS

    def start_requests(self):
        yield scrapy.Request('http://et-stage.net/eventList.php')

    def parse(self, response):
        if 'eventList.php' in response.url:
            return self.parseList(response)
        elif '/event/' in response.url:
            return self.parseEvent(response)

    def parseList(self, response):
        urls = response.css('div.event-list').xpath('./a/@href').extract()
        for url in urls:
            yield scrapy.Request(self.abs_url(response, url))

    def parseDateTimes(self, content_date):
        if ' ' in content_date:
            date_string, times_string = content_date.split(' ', 1)
        else:
            date_string = content_date
            times_string = ''
        date = datetime.datetime.strptime(date_string.strip(), '%Y.%m.%d').date()
        return jp_spider.parse_date_times(date, times_string.strip())

    def parseEvent(self, response):
        def _get(css_id):
            return items.extract_text(response.css('#%s' % css_id))

        item = items.WebEvent()
        item['country'] = 'JP'
        item['namespace'] = self.namespace
        item['namespaced_id'] = re.search(r'/event/(\w+)/', response.url).group(1)

        item['description'] = items.extract_text(response.css('div.eventdetail'))

        tds = response.css('div.visible-xs table.table td')
        if len(tds) != 6:
            logging.error('Problem with unknown %s tds:\n%s', len(tds), '\n'.join(str(x) for x in tds))

        item['name'] = items.extract_text(tds[0].xpath('.//text()'))
        item['start_time'], item['end_time'] = self.parseDateTimes(items.extract_text(tds[1].xpath('.//text()')))
        venue = items.extract_text(tds[2].xpath('.//text()'))
        address = items.extract_text(tds[3].xpath('.//text()'))
        if not venue:
            venue = jp_spider.get_venue_from_description(item['description'])
        jp_addresses = japanese_addresses.find_addresses(address)
        jp_spider.setup_location(venue, jp_addresses, item)

        image_elements = response.xpath("//img[@data-target='#image_Modal']/@src").extract()
        if image_elements:
            image_url = image_elements[0]
            image_url = self.abs_url(response, image_url)
        else:
            image_url = None
        item['photo'] = image_url

        yield item
