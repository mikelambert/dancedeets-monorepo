import dateparser
import datetime
import re
import urlparse
import urllib

import scrapy

from .. import items


def parse_times(date, times):
    start_time_string, end_time_string = re.split(r' - ', times)
    start_time = dateparser.parse(start_time_string).time()
    end_time = dateparser.parse(end_time_string).time()
    return start_time, end_time


class BdcDay(items.StudioScraper):
    name = 'BDC'
    allowed_domains = ['broadwaydancecenter.com']
    latlong = (40.7594536, -73.9918209)
    address = '322 W 45th St, New York, NY'

    def start_requests(self):
        for i in range(2):
            d = datetime.datetime.today() + datetime.timedelta(days=7)
            bdc_args = {
                'date[value][date]': d.strftime('%m/%d/%Y'),
                'style': 'All',
                'level': 'All',
                'instructor': 'All',
            }
            yield scrapy.Request('http://www.broadwaydancecenter.com/week-schedule?%s' % urllib.urlencode(bdc_args))

    _acronyms = {
        'Beg': 'Beginner',
        'Int': 'Intermediate',
        'Adv': 'Advanced',
    }

    @classmethod
    def _expand_acronyms(cls, s):
        for k, v in cls._acronyms.items():
            s = re.sub(r'\b%s\b' % k, v, s)
        return s

    def parse_classes(self, response):
        date_tables = response.css('table.table-hoverviews-table')
        for table in date_tables:
            date_string = table.xpath('./caption/a/text()').extract()[0]
            date = dateparser.parse(date_string).date()

            for class_row in table.xpath('./tbody/tr'):
                times_string = class_row.xpath('./td[0]/text()').extract()[0]
                class_name = class_row.xpath('./td[1]/text()').extract()[0]
                teacher_name = class_row.xpath('./td[1]/div//text()').extract()[0]
                teacher_rel_link = class_row.xpath('./td[1]/div//@href').extract()[0]
                class_level = class_row.xpath('./td[2]/text()').extract()[0]

                if not self._street_style(class_name):
                    continue

                item = items.StudioClass()
                start_time, end_time = parse_times(times_string)
                item['start_time'] = datetime.datetime.combine(date, start_time)
                item['end_time'] = datetime.datetime.combine(date, end_time)

                class_title = self._expand_acronyms(class_name).title()
                class_title = class_title.split(' With ')[0]
                class_title = class_title + ' (%s)' % class_level
                item['style'] = class_title
                item['teacher'] = teacher_name

                if teacher_rel_link:
                    item['teacher_link'] = urlparse.urljoin(response.url, teacher_rel_link)

                yield item
