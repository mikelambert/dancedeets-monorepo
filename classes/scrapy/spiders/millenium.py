import dateparser
import datetime

from .. import items

def extract_text(cell):
    return ' '.join(cell.xpath('.//text()').extract()).strip()

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
                date_string = extract_text(row.css('.hc_date'))
                date = dateparser.parse(date_string).date()
            else:
                class_types = extract_text(row.css('span.type_group'))
                if 'Adult Program' not in class_types:
                    continue
                style = extract_text(row.css('span.classname::text'))
                if not self._street_style(style):
                    continue

                item = items.StudioClass()
                start_time_str = row.css('.hc_starttime::text').extract()[0]
                end_time_str = row.css('.hc_endtime::text').extract()[0].replace(' - ', '')
                start_time = dateparser.parse(start_time_str).time()
                end_time = dateparser.parse(end_time_str).time()
                item['start_time'] = datetime.datetime.combine(date, start_time)
                item['end_time'] = datetime.datetime.combine(date, end_time)
                item['style'] = style
                item['teacher'] = extract_text(row.css('span.trainer'))

                yield item
