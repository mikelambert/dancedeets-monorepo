# -*- coding: utf-8 -*-

import dateparser
import datetime
import json
import logging
import re
import scrapy

from .. import items

def parse_times(dt):
    day, times = dt.split(' ', 1)
    date = dateparser.parse(day)
    start_time_string, end_time_string = re.split(r'-', times, 1)
    start_time = dateparser.parse(start_time_string).time()
    end_time = dateparser.parse(end_time_string).time()
    if start_time.hour < 12:
        start_time = start_time.replace(start_time.hour + 12)
    if end_time.hour < 12:
        end_time = end_time.replace(end_time.hour + 12)
    return (
        datetime.datetime.combine(date, start_time),
        datetime.datetime.combine(date, end_time),
    )


class TheLab(items.StudioScraper):
    name = 'TheLab'
    allowed_domains = ['www.tlxwc.com']
    latlong = (34.080570991151, -117.90854036514)
    address = '541 N Azusa Ave, West Covina, CA'

    def start_requests(self):
        yield scrapy.Request('http://www.tlxwc.com/wp/?page_id=79')

    def _valid_item(self, item):
        if not self._street_style(item['style']):
            return False
        return True

    def parse_classes(self, response):
        logging.info(response)
        for col in response.css('div.wpb_text_column'):
            col_text = self._extract_text(col)
            if 'BEGINNING' in col_text or 'ADVANCED' in col_text:
                for row in col.css('p'):
                    text = self._extract_text(row)
                    if u'–' in text and re.search('\d:\d\d', text):
                        datetime, class_details = text.split(u'–', 1)

                        teacher_match = re.search(r'\((.+?)\)', class_details.strip())
                        if teacher_match:
                            teacher = teacher_match.group(1)
                        else:
                            logging.error('Could not find teacher: %s', class_details)
                            teacher = ''
                        class_details = re.sub('\(%s\)' % teacher, '', class_details)

                        item = items.StudioClass()
                        item['style'] = class_details.title()
                        item['teacher'] = teacher.title()
                        # do we care?? row[4]
                        start_time, end_time = parse_times(datetime.strip())
                        item['start_time'] = start_time
                        item['end_time'] = end_time
                        if self._valid_item(item):
                            for new_item in self._repeated_items_iterator(item):
                                yield new_item
