# -*-*- encoding: utf-8 -*-*-

import datetime
import re
import urlparse

import html2text
import scrapy

from loc import gmaps
from .. import items


date_re = ur'(\d\d\d\d)(?:年|\s*[/.]|)\s*(\d\d?)(?:月|\s*[/.]|)\s*(\d\d?)日?'
open_time_re = ur'OPEN\W+\b(\d+):(\d+)\b|(\d+):(\d+)\W+OPEN'
close_time_re = ur'CLOSE\W+\b(\d+):(\d+)\b'
open_close_time_re = ur'(\d+):(\d+)～(\d+):(\d+)'


def _intall(lst):
    return [None if x is None else int(x) for x in lst]


def parse_date_times(date_str):
    date_str = date_str.upper()
    start_date = datetime.date(*_intall(re.search(date_re, date_str).groups()))

    open_time = None
    close_time = None

    open_match = re.search(open_time_re, date_str)
    if open_match:
        open_time = _intall(open_match.groups())
        close_match = re.search(close_time_re, date_str)
        if close_match:
            close_time = _intall(close_match.groups())

    open_close_match = re.search(open_close_time_re, date_str)
    if open_close_match:
        open_close_time = _intall(open_close_match.groups())
        open_time = open_close_time[0:2]
        close_time = open_close_time[2:4]

    start_datetime = start_date
    if open_time:
        # We use timedelta instead of time, so that we can handle hours=24 or hours=25 as is sometimes used in Japan
        start_timedelta = datetime.timedelta(hours=open_time[0], minutes=open_time[1])
        start_datetime = datetime.datetime.combine(start_date, datetime.time()) + start_timedelta

    end_datetime = None
    if close_time:
        end_timedelta = datetime.timedelta(hours=close_time[0], minutes=close_time[1])
        end_datetime = datetime.datetime.combine(start_date, datetime.time()) + end_timedelta
        if end_datetime < start_datetime:
            end_datetime += datetime.timedelta(days=1)

    return start_datetime, end_datetime


# TODO: move to test file
tests = {
    u"""2016年3月25日（金）
    OPEN 12:00
    CLOSE 19:00""":
    (datetime.datetime(2016, 3, 25, 12), datetime.datetime(2016, 3, 25, 19)),
    u"""2016/3/27（日曜）
    12:00～22:00""":
    (datetime.datetime(2016, 3, 27, 12), datetime.datetime(2016, 3, 27, 22)),
    u"""2016/3/26[SAT]
    13:00～20:30""":
    (datetime.datetime(2016, 3, 26, 13), datetime.datetime(2016, 3, 26, 20, 30)),
    u"""2016年3月5日(土)
    OPEN 12:00 START 13:00""":
    (datetime.datetime(2016, 3, 5, 12), None),
    # http://www.tokyo-dancelife.com/event/2016_03/29491.php
    u"""2016年3月5日(土)
    ...and later in the body/description:
    【日本代表決定戦】
    OPEN 14:30 START 15:00""":
    (datetime.datetime(2016, 3, 5, 14, 30), None),
    u"""2016年3月5日(土)""":
    (datetime.date(2016, 3, 5), None),
}

for test, expected_result in tests.iteritems():
    result = parse_date_times(test)
    if result != expected_result:
        print "ERROR:"
        print test
        print result
        print expected_result


def html_to_newlines(html):
    return html2text.html2text(html).replace('\n\n', '\n')


class TokyoDanceLifeScraper(items.WebEventScraper):
    name = 'TokyoDanceLife'
    allowed_domains = ['www.tokyo-dancelife.com']

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
                yield scrapy.Request(urlparse.urljoin(response.url, url))

        event_urls = response.xpath('//div[@class="name"]/a/@href').extract()
        for url in event_urls:
            yield scrapy.Request(urlparse.urljoin(response.url, url))

    def parseEvent(self, response):
        print response.url

        item = items.WebEvent()
        item['id'] = re.search(r'/(\d+)\.php', response.url).group(1)
        item['website'] = self.name
        item['title'] = self._extract_text(response.css('div.event-detail-name'))

        photos = response.css('div.event-detail-img').xpath('./a/@href').extract()
        if photos:
            item['photo'] = photos[0]
        else:
            item['photo'] = None

        category = response.css('div.event-detail-koumoku').xpath('./img/@alt').extract()[0]
        print category.encode('utf-8')
        #TODO!!!

        class Definitions(object):
            def __init__(self, dl):
                self.dl = dl
                self.dl_text = dl.extract()[0]

            def _term(self, term):
                return self.dl.xpath(u'//dt[contains(., "%s")]' % term)

            def _definition(self, term):
                return self.dl.xpath(u'//dt[contains(., "%s")]/following-sibling::dd[1]' % term)

            def extract_definition(self, term):
                found_term = self._definition(term).extract()
                if not found_term:
                    return None
                value = html_to_newlines(found_term[0]).strip()
                self.dl_text = self.dl_text.replace(self._definition(term).extract()[0], "")
                self.dl_text = self.dl_text.replace(self._term(term).extract()[0], "")
                return value

            def get_remaining_dl(self):
                return self.dl_text

        dl = Definitions(response.xpath('//dl'))
        start_date = dl.extract_definition(u'日程')
        venue_address = dl.extract_definition(u'場所')

        if venue_address:
            venue_components = [x.strip() for x in venue_address.split('\n')]
            if len(venue_components) == 2:
                item['location_name'], item['location_address'] = venue_components
            else:
                item['location_name'] = venue_components[0]
                results = gmaps.fetch_places_raw(query='%s, japan' % item['location_name'])
                if results['status'] == 'ZERO_RESULTS':
                    results = gmaps.fetch_places_raw(query=item['location_name'])
                if results['status'] != 'ZERO_RESULTS':
                    item['location_address'] = results['results'][0]['formatted_address']
                    latlng = results['results'][0]['geometry']['location']
                    item['latitude'] = latlng['lat']
                    item['longitude'] = latlng['lng']

        main_description = dl.extract_definition(u'詳細')
        description = main_description
        # Because dt otherwise remains flush up against the end of the previous dd, we insert manual breaks.
        description += html_to_newlines(dl.get_remaining_dl().replace('<dt>', '<dt><br><br>'))
        item['description'] = description

        if not start_date:
            raise ValueError()

        try:
            item['starttime'], item['endtime'] = parse_date_times(start_date)
        except:
            item['starttime'], item['endtime'] = parse_date_times(start_date + '\n\n' + description)
        #item['latitude'] = latlng['lat']
        #item['longitude'] = latlng['lng']

        yield item
