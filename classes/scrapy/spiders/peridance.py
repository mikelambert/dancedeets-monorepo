import dateparser
import datetime
import urlparse

import scrapy

from .. import items

def parse_times(times):
    start, end = times.split(u'\xa0-\xa0')
    return dateparser.parse(start).time(), dateparser.parse(end).time()

class PeridanceDay(items.StudioScraper):
    name = 'Peridance'
    allowed_domains = ['peridance.com']
    latlong = (40.7328217, -73.9907902)
    address = '126-128 E 13th St, New York, NY'

    def start_requests(self):
        today = datetime.date.today()
        for i in range(7):
            date_string = (today + datetime.timedelta(days=i)).strftime('%m/%d/%Y')
            yield scrapy.Request('http://www.peridance.com/openclasses.cfm?testdate=%s' % date_string)

    def parse_classes(self, response):
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
                start_time, end_time = parse_times(times)
                item['start_time'] = datetime.datetime.combine(date, start_time)
                item['end_time'] = datetime.datetime.combine(date, end_time)
                item.add('style', row.xpath('.//td[2]//text()'))
                item.add('teacher', row.xpath('.//td[3]//text()'))
                hrefs = row.xpath('.//td[3]//@href').extract()
                if hrefs:
                    url = urlparse.urljoin(response.url, hrefs[0])
                    item['teacher_link'] = url

                yield item
