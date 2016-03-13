# -*-*- encoding: utf-8 -*-*-

import datetime
import re
import urlparse

import scrapy
from scrapy.selector import Selector

from .. import items
from .. import jp_spider

date_re = ur'(\d+)年\s*(\d+)月\s*(\d+)日'
# We separate these so we can handle "OPEN : 12:00 / 14:30 / CLOSE : 14:30 / 16:00"
open_time_re = ur'OPEN : (\d+):(\d+) ' # first open time
close_time_re = ur'CLOSE : .*\b(\d+):(\d+)\b' # last close time


def parse_date_times(date_str, time_str):
    start_date = datetime.date(*jp_spider._intall(re.search(date_re, date_str).groups()))
    if time_str:
        open_time = jp_spider._intall(re.search(open_time_re, time_str).groups())

        # We use timedelta instead of time, so that we can handle hours=24 or hours=25 as is sometimes used in Japan
        start_timedelta = datetime.timedelta(hours=open_time[0], minutes=open_time[1])
        start_datetime = datetime.datetime.combine(start_date, datetime.time()) + start_timedelta
        close_match = re.search(close_time_re, time_str)
        if close_match:
            close_time = jp_spider._intall(close_match.groups())
            end_timedelta = datetime.timedelta(hours=close_time[0], minutes=close_time[1])
            end_datetime = datetime.datetime.combine(start_date, datetime.time()) + end_timedelta
            if end_datetime < start_datetime:
                end_datetime += datetime.timedelta(days=1)
            return start_datetime, end_datetime
        else:
            return start_datetime, None
    else:
        return start_date, None


class DewsScraper(items.WebEventScraper):
    name = 'Dews'
    allowed_domains = ['dews365.com']

    def start_requests(self):
        yield scrapy.Request('http://dews365.com/eventinformation')

    def parse(self, response):
        if 'eventinformation' in response.url:
            return self.parseList(response)
        elif '/event/' in response.url:
            return self.parseEvent(response)

    def parseList(self, response):
        urls = response.xpath('//a/@href').extract()
        for url in [x for x in urls if '/event/' in x]:
            yield scrapy.Request(urlparse.urljoin(response.url, url))

        next_urls = response.xpath('//a[@rel="next"]/@href').extract()
        for url in next_urls:
            yield scrapy.Request(urlparse.urljoin(response.url, url))

    def _get_description(self, response):
        description_paragraphs = response.css('div.detail').xpath('./following-sibling::p').extract()
        description_list = []
        for p in description_paragraphs:
            description_list.append('\n\n')
            elems = Selector(text=p).xpath('//text()|//br').extract()
            elems = [x for x in [self._cleanup(x).strip() for x in elems] if x]
            elems = ['\n' if x == '<br>' else x for x in elems]
            description_list.extend(elems)
        description = ''.join(description_list).strip()
        return description

    def parseEvent(self, response):
        def _get(propname, attr=None):
            node = response.xpath('//*[@itemprop="%s"]' % propname)
            if attr:
                return node.xpath('./@%s' % attr).extract()[0]
            else:
                return self._extract_text(node)

        def _definition(term):
            return self._extract_text(response.xpath(u'//dt[contains(., "%s")]/following-sibling::dd' % term))

        item = items.WebEvent()
        item['id'] = re.search(r'/event/(\w+)\.html', response.url).group(1)
        item['website'] = self.name
        item['title'] = _get('name')
        item['photo'] = _get('image', 'content')

        genre = _definition(u'ジャンル')
        description = self._get_description(response)
        item['description'] = genre + description

        item['starttime'], item['endtime'] = parse_date_times(_get('startDate'), _definition(u'時間'))

        jp_spider.setup_location(_get('location'), None, item)

        yield item
