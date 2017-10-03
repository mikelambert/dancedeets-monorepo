# -*-*- encoding: utf-8 -*-*-

import dateparser
import datetime
import scrapy
import scrapyjs

from .. import items

from dancedeets.nlp import event_classifier
from dancedeets.nlp import rules


def parse_times(times):
    start_string, end_string = times.split(' - ')
    start_time = dateparser.parse(start_string + ' pm').time()
    end_time = dateparser.parse(end_string).time()
    return start_time, end_time


class PMTHouseOfDance(items.StudioScraper):
    name = 'PMT'
    allowed_domains = ['pmthouseofdance.com']
    latlong = (40.7374272, -73.9987284)
    address = '69 W 14th St, New York, NY'

    def start_requests(self):
        yield scrapy.Request('http://www.pmthouseofdance.com/general-schedule?_escaped_fragment_=')

    def parse_classes(self, response):
        table = response.css('table')

        date = None  # Keep track of this row-to-row
        for row in table.css('tr'):
            cells = row.css('td')
            if not cells:
                continue

            row_contents = self._extract_text(row)
            if not row_contents or '---' in row_contents:
                continue

            potential_day = self._extract_text(cells[0])
            if potential_day:
                date = dateparser.parse(potential_day).date()
            times = self._extract_text(cells[1])
            classname = self._extract_text(cells[2])

            if not times:
                continue

            teacher = self._extract_text(cells[3])
            teacher_href = cells[3].xpath('.//@href').extract()[0].strip()

            # Use our NLP event classification keywords to figure out which BDC classes to keep
            processor = event_classifier.StringProcessor(classname)
            if not processor.has_token(rules.DANCE_STYLE):
                continue

            item = items.StudioClass()
            item['style'] = classname
            item['teacher'] = teacher
            item['teacher_link'] = teacher_href
            # do we care?? row[4]
            start_time, end_time = parse_times(self._cleanup(times))
            item['start_time'] = datetime.datetime.combine(date, start_time)
            item['end_time'] = datetime.datetime.combine(date, end_time)
            for new_item in self._repeated_items_iterator(item):
                yield new_item
