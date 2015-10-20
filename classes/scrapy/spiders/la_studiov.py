import dateparser
import datetime

from .. import items

def parse_times(times):
    start, end = times.split(u' - ')
    return dateparser.parse(start).time(), dateparser.parse(end).time()

def extract_text(cell):
    return ' '.join(cell.xpath('.//text()').extract()).strip()

class StudioV(items.StudioScraper):
    name = 'StudioV'
    allowed_domains = ['la.thestudiov.com']
    latlong = (34.188804, -118.3895947)
    address = '7746 Gloria Ave, Van Nuys, CA 91406'

    start_urls = [
        'http://la.thestudiov.com/classes/',
    ]

    def parse_classes(self, response):
        date = dateparser.parse('thursday').date()
        if date < datetime.date.today():
            date += datetime.timedelta(days=7)
        tbody = response.css('.row-hover')
        for row in tbody.css('tr'):
            times, style, teacher = [extract_text(x) for x in row.css('td')]
            start_time, end_time = parse_times(times)

            item = items.StudioClass()
            item['start_time'] = datetime.datetime.combine(date, start_time)
            item['end_time'] = datetime.datetime.combine(date, end_time)
            item['style'] = style
            item['teacher'] = teacher
            yield item
