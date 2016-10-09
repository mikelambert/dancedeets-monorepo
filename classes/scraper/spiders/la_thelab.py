# -*- coding: utf-8 -*-

import dateparser
import datetime
import json
import re
import scrapy

from .. import items

import facebook
token = facebook._PROD_FACEBOOK_CONFIG['app_access_token']


def parse_times(times):
    start_time_string, end_time_string = re.split(r'-', times, 1)
    start_time = dateparser.parse(start_time_string).time()
    end_time = dateparser.parse(end_time_string).time()
    if start_time.hour < 12:
        start_time = start_time.replace(start_time.hour + 12)
    if end_time.hour < 12:
        end_time = end_time.replace(end_time.hour + 12)
    return start_time, end_time


class TheLab(items.StudioScraper):
    name = 'TheLab'
    allowed_domains = ['graph.facebook.com']
    latlong = (34.080570991151, -117.90854036514)
    address = '541 N Azusa Ave, West Covina, CA'

    def start_requests(self):
        yield scrapy.Request('https://graph.facebook.com/v2.7/InTheLab247?fields=general_info&access_token=' + token)

    def _get_url(self, response):
        return 'https://www.facebook.com/InTheLab247'

    def _valid_item(self, item):
        if not self._street_style(item['style']):
            return False
        return True

    def parse_classes(self, response):
        classes = json.loads(response.body)
        for line in classes['general_info'].splitlines():
            if u' – ' not in line:
                continue
            daytimes, description = line.split(u' – ', 1)
            match = re.search('\((.*?)\)', description)
            teacher = match.group(1)
            description = description.replace('(%s)' % teacher, '')
            item = items.StudioClass()
            item['style'] = description.title().strip()
            item['teacher'] = teacher.title()
            day, times = daytimes.split(' ')
            start_time, end_time = parse_times(times)
            date = dateparser.parse(day).date()
            item['start_time'] = datetime.datetime.combine(date, start_time)
            item['end_time'] = datetime.datetime.combine(date, end_time)
            if not self._valid_item(item):
                continue
            for new_item in self._repeated_items_iterator(item):
                yield new_item
