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
                times = row.xpath('.//td[1]/text()').extract()[0]
                if times == 'Time':
                    continue
                item = items.StudioClass()
                item['source_page'] = response.url
                start_time, end_time = parse_times(times)
                item['start_time'] = datetime.datetime.combine(date, start_time)
                item['end_time'] = datetime.datetime.combine(date, end_time)
                item.add'style', row.xpath('.//td[2]//text()'))
                item.add('teacher', row.xpath('.//td[3]//text()'))
                item.add('teacher_link', row.xpath('.//td[3]//@href'))
                yield l.polish()
