import dateparser
import datetime
import scrapy
from .. import items

def parse_times(times):
    start, end = times.split(u'\xa0-\xa0')
    return dateparser.parse(start).time(), dateparser.parse(end).time()

class PeridanceDay(scrapy.Spider):
    name = 'Peridance'
    allowed_domains = ['peridance.com']
    start_urls = [
        'http://www.peridance.com/openclasses.cfm',
#        'http://www.peridance.com/curriculum.cfm?DTID=28&dancetype=Hip%20Hop',
    ]

    def parse(self, response):
        date_string = response.xpath('//pagesubtitle/text()').extract()[0]
        date_string = date_string.replace('Open Classes for ', '')
        date = dateparser.parse(date_string).date() 
        
        table = response.selector.xpath('//table[@width="540"]')
        for row in table.xpath('.//tr'):
            colspan3 = row.xpath('./td[@colspan="3"]')
            if colspan3:
                header = ''.join(colspan3.xpath('.//text()').extract()).strip()
            else:
                if 'Street' not in header:
                    continue
                l = items.ClassLoader(item=items.ClassItem(), selector=row)
                l.add_value('source_page', response.url)
                times = row.xpath('.//td[1]/text()').extract()[0]
                if times == 'Time':
                    continue
                print times
                start_time, end_time = parse_times(times)
                l.add_value('start_time', datetime.datetime.combine(date, start_time))
                l.add_value('end_time', datetime.datetime.combine(date, end_time))
                l.add_xpath('style', './/td[2]//text()')
                l.add_xpath('teacher', './/td[3]//text()')
                l.add_xpath('teacher_link', './/td[3]//@href')
                yield l.load_item()
