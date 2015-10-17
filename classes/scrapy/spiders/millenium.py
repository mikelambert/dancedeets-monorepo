import dateparser
import datetime
import urlparse

import scrapy

from .. import items
from nlp import event_classifier
from nlp import keywords
from nlp import rules

class Millenium(items.StudioScraper):
    name = 'Millenium'
    allowed_domains = ['healcode.com']
    latlong = (34.1633887, -118.3763954)
    address = '5113 Lankershim Blvd., North Hollywood, CA 91601'

    start_urls = [
        'https://widgets.healcode.com/widgets/schedules/print/8113116c418',
    ]

    def parse_classes(self, response):
        table = response.css('table.schedule')
        for row in table.xpath('.//tr'):
            class_value = row.xpath('@class').extract()[0]
            classes = class_value.split(' ')
            if 'schedule_header' in classes:
                date_string = row.css('.hc_date').xpath('.//text()').extract()[0]
                date = dateparser.parse(date_string).date()
            else:
                class_types = row.css('span.type_group').xpath('.//text()').extract()
                if 'Adult Program' not in class_types:
                    continue
                style = ' '.join(row.css('span.classname::text').xpath('.//text()').extract()).strip()
                # Use our NLP event classification keywords to figure out which BDC classes to keep
                processor = event_classifier.StringProcessor(style)
                # Get rid of "Ballet with Pop Music"
                processor.real_tokenize(keywords.PREPROCESS_REMOVAL)
                if not processor.has_token(rules.DANCE_STYLE):
                    continue

                item = items.StudioClass()
                start_time_str = row.css('.hc_starttime::text').extract()[0]
                end_time_str = row.css('.hc_endtime::text').extract()[0].replace(' - ', '')
                start_time = dateparser.parse(start_time_str).time()
                end_time = dateparser.parse(end_time_str).time()
                item['start_time'] = datetime.datetime.combine(date, start_time)
                item['end_time'] = datetime.datetime.combine(date, end_time)
                item['style'] = style
                item['teacher'] = ' '.join(row.css('span.trainer').xpath('.//text()').extract()).strip()

                yield item
