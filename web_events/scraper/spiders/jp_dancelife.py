# -*-*- encoding: utf-8 -*-*-

import datetime
import re
import urlparse

import scrapy

from loc import japanese_addresses
from loc import gmaps
from .. import items


date_re = ur'(\d\d\d\d)(?:年|\s*[/.]|)\s*(\d\d?)(?:月|\s*[/.]|)\s*(\d\d?)日?'
open_time_re = ur'OPEN\W+\b(\d\d?):(\d\d)\b|(\d\d?):(\d\d)\W*OPEN|(\d\d?):(\d\d)\s*～'
close_time_re = ur'CLOSE(?:\s*予定)?\W+\b(\d+):(\d\d)\b'
open_close_time_re = ur'(\d\d?):(\d\d)\s*～\s*(\d\d?):(\d\d)'


def _intall(lst):
    return [None if x is None else int(x) for x in lst]


def parse_date_times(start_date, date_str):

    open_time = None
    close_time = None

    open_match = re.search(open_time_re, date_str)
    if open_match:
        open_time = _intall(open_match.groups())
        # Keep trimming off groups of 2 until we find valid values
        while open_time[0] is None:
            open_time = open_time[2:]
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


def html_to_newlines(html):
    return items._format_text(html)


def _get_line_after(text, regex):
    desc_lines = text.split('\n')
    return_next_line = False
    for line in desc_lines:
        if return_next_line:
            if line:
                return line
        if re.search(regex, line):
            after_keyword = re.split(regex, line, 1)[1]
            # If it's a "keyword: something"...return the same line
            if len(after_keyword) > 4:
                return after_keyword.replace(u'：', '').strip()
            return_next_line = True
    return None


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
        PAST_EVENTS = True
        if PAST_EVENTS:
            monthly_page_urls = response.css('div#pastevent-area').xpath('.//a/@href').extract()
            for url in monthly_page_urls:
                yield scrapy.Request(urlparse.urljoin(response.url, url))

        event_urls = response.xpath('//div[@class="name"]/a/@href').extract()
        for url in event_urls:
            yield scrapy.Request(urlparse.urljoin(response.url, url))

    def parseDateTimes(self, response):
        day_text = self._extract_text(response.css('div.day'))
        month, day = re.search(r'(\d+)\.(\d+)', day_text).groups()
        year = re.search(r'/(\d\d\d\d)_\d+/', response.url).group(1)
        start_date = datetime.date(int(year), int(month), int(day))

        return parse_date_times(start_date, self._extract_text(response.xpath('//dl')))

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
        # Because dt otherwise remains flush up against the end of the previous dd, we insert manual breaks.
        full_description = html_to_newlines(response.xpath('//dl').extract()[0].replace('<dt>', '<dt><br><br>'))
        item['description'] = '%s\n\n%s' % (category, full_description)

        jp_addresses = japanese_addresses.find_addresses(item['description'])
        if jp_addresses:
            item['location_address'] = jp_addresses[0]

        venue_address = _get_line_after(item['description'], ur'場所|会場')
        if venue_address:
            # remove markdown bolding
            item['location_name'] = venue_address.replace('**', '')

        if 'location_name' in item and 'location_address' not in item:
            # Let's look it up on Google
            results = {'status': 'FAIL'}
            #results = gmaps.fetch_places_raw(query='%s, japan' % item['location_name'])
            if results['status'] == 'ZERO_RESULTS':
                results = gmaps.fetch_places_raw(query=item['location_name'])
            if results['status'] == 'OK':
                item['location_address'] = results['results'][0]['formatted_address']
                latlng = results['results'][0]['geometry']['location']
                item['latitude'] = latlng['lat']
                item['longitude'] = latlng['lng']

        item['starttime'], item['endtime'] = self.parseDateTimes(response)

        #item['latitude'] = latlng['lat']
        #item['longitude'] = latlng['lng']

        yield item
