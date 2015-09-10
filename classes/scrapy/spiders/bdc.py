import dateparser
import datetime
import re
import scrapy
from .. import items

"""
class BdcStyle(scrapy.Spider):
    name = 'broadwaydancecenter.com/style'
    allowed_domains = ['broadwaydancecenter.com']
    start_urls = [
        'http://www.broadwaydancecenter.com/schedule/schedule_hiphop.shtml',
    ]

    def parse(self, response):
        self.logger.info('A response from %s just arrived!', response.url)
"""

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

class BdcDay(scrapy.Spider):
    name = 'BDC'
    allowed_domains = ['broadwaydancecenter.com']
    start_urls = [
        'http://www.broadwaydancecenter.com/schedule/9_9.shtml',
    ]

    def parse(self, response):
        table = response.css('table.grid table.grid')
        self.logger.info('%s', table)
        date_string = table.css('.gridDateTitle').xpath('.//text()').extract()[0]
        date = dateparser.parse(date_string).date() 
        for row in table.xpath('.//tr'):
            l = items.ClassLoader(item=items.ClassItem(), selector=row)
            l.add_value('source_page', response.url)
            if not row.xpath('.//td[1]/text()'):
                continue
            times = row.xpath('.//td[1]/text()').extract()[0]
            if '-' not in times:
                continue
            start_time, end_time = parse_times(times)
            l.add_value('start_time', datetime.datetime.combine(date, start_time))
            l.add_value('end_time', datetime.datetime.combine(date, end_time))
            l.add_xpath('style', './/td[2]/text() | .//td[3]/text()')
            l.add_xpath('teacher', './/td[4]//text()')
            l.add_xpath('teacher_link', '(.//td[4]//@href)[1]')
            yield l.load_item()
