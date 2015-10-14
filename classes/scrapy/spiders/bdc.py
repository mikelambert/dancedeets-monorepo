import dateparser
import datetime
import re
import urlparse

import scrapy

from .. import items
from nlp import event_classifier
from nlp import keywords
from nlp import rules

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

            # Use our NLP event classification keywords to figure out which BDC classes to keep
            just_style = row.xpath('.//td[2]/text()').extract()[0]
            processor = event_classifier.StringProcessor(just_style)
            # Get rid of "Ballet with Pop Music"
            processor.real_tokenize(keywords.PREPROCESS_REMOVAL)
            if not processor.has_token(rules.DANCE_STYLE):
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
