# -*-*- encoding: utf-8 -*-*-

import datetime
import re
import urlparse

import scrapy

from .. import items


time_re = ur'(\d+)時(\d+)分'
date_time_re = ur'(\d+)年(\d+)月(\d+)日 %s' % time_re


def _intall(lst):
    return [int(x) for x in lst]


def parse_times(s):
    # '2016年03月09日 23時30分～2016年03月10日 05時30分'
    # '2016年03月10日 20時00分～23時30分'
    start_str, end_str = s.split(u'～')
    start_match = re.match(date_time_re, start_str)
    if not start_match:
        raise ValueError("Could not parse start time: %s" % start_str)
    start_datetime = datetime.datetime(*_intall(start_match.groups()))

    end_match = re.match(date_time_re, end_str)
    if end_match:
        end_datetime = datetime.datetime(*_intall(end_match.groups()))
    else:
        end_match = re.match(time_re, end_str)
        if end_match:
            end_time = datetime.time(*_intall(end_match.groups()))
            end_datetime = datetime.datetime.combine(start_datetime.date(), end_time)
        else:
            raise ValueError("Could not parse end time: %s" % end_str)
    return (start_datetime, end_datetime)


class EnterTheStageScraper(items.WebEventScraper):
    name = 'EnterTheStage'
    allowed_domains = ['et-stage.net']

    def start_requests(self):
        yield scrapy.Request('http://et-stage.net/event_list.php')

    def parse(self, response):
        if 'event_list.php' in response.url:
            return self.parseList(response)
        elif '/event/' in response.url:
            return self.parseEvent(response)

    def parseList(self, response):
        urls = response.xpath('//a[@class="block"]/@href').extract()
        for url in urls:
            yield scrapy.Request(urlparse.urljoin(response.url, url))

    def parseEvent(self, response):
        def _get(css_id):
            return self._extract_text(response.css('#%s' % css_id))

        item = items.WebEvent()
        item['id'] = re.search(r'/event/(\w+)/', response.url).group(1)
        item['website'] = self.name
        item['title'] = _get('u474-4')
        image_url = response.xpath('//img[@id="u469_img"]/@src').extract()[0]
        item['photo'] = urlparse.urljoin(response.url, image_url)

        # cost = _get('u511-7')
        # email = _get('u512-4')

        item['description'] = _get('u468-156')
        item['starttime'], item['endtime'] = parse_times(_get('u506-2'))

        item['location_name'] = _get('u507-4')
        item['location_address'] = _get('u509-11')

        yield item
