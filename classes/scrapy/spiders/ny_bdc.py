import dateparser
import datetime
import re
import urlparse

import scrapy

from .. import items

def parse_time(ts):
    if re.search(r'noon|am|pm', ts.lower()):
        return dateparser.parse(ts).time(), True
    else:
        return dateparser.parse(ts).time(), False

def format_tuple_as_time_using_time(unsure_time, time):
    formatted_time = '%s %s' % (unsure_time.strftime('%I:%M'), time.strftime('%p'))
    return dateparser.parse(formatted_time).time()

def parse_times(times):
    start_time_string, end_time_string = re.split(r' ?- ?', times)
    start_time, start_time_correct = parse_time(start_time_string)
    end_time, end_time_correct = parse_time(end_time_string)
    if not start_time_correct:
        start_time = format_tuple_as_time_using_time(start_time, end_time)
    elif not end_time_correct:
        end_time = format_tuple_as_time_using_time(end_time, start_time)
    return start_time, end_time

class BdcDay(items.StudioScraper):
    name = 'BDC'
    allowed_domains = ['broadwaydancecenter.com']
    latlong = (40.7594536, -73.9918209)
    address = '322 W 45th St, New York, NY'

    def start_requests(self):
        today = datetime.date.today()
        for i in range(7):
            date_string = (today + datetime.timedelta(days=i)).strftime('%m_%d')
            yield scrapy.Request('http://www.broadwaydancecenter.com/schedule/%s.shtml' % date_string)


    def parse_classes(self, response):
        table = response.css('table.grid table.grid')
        # Oh BDC you have such strange HTML variations sometimes
        if not table:
            table = response.css('table.grid')
        date_string = table.css('.gridDateTitle').xpath('.//text()').extract()[0]
        date = dateparser.parse(date_string).date()
        for row in table.xpath('.//tr'):
            if not row.xpath('.//td[1]/text()'):
                continue
            times = row.xpath('.//td[1]/text()').extract()[0]
            if '-' not in times:
                continue

            just_style = row.xpath('.//td[2]/text()').extract()[0]
            if not self._street_style(just_style):
                continue

            item = items.StudioClass()
            start_time, end_time = parse_times(times)
            item['start_time'] = datetime.datetime.combine(date, start_time)
            item['end_time'] = datetime.datetime.combine(date, end_time)

            item.add('style', row.xpath('.//td[2]/text() | .//td[3]/text()'))
            item.add('teacher', row.xpath('.//td[4]//text()'))
            url = urlparse.urljoin(response.url, row.xpath('(.//td[4]//@href)[1]').extract()[0])
            item['teacher_link'] = url

            yield item
