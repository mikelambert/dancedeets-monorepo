import dateparser
import datetime
import re

from .. import items

class NeighborhoodStudio(items.StudioScraper):
    name = 'NeighborhoodStudio'
    allowed_domains = ['healcode.com']
    latlong = (34.0237478, -118.384045)
    address = '3625 Hayden Ave, Culver City, CA 90232'

    start_urls = [
        'https://widgets.healcode.com/widgets/schedules/print/2961706fc',
    ]

    def parse_classes(self, response):
        table = response.css('table.schedule')
        for row in table.xpath('.//tr'):
            class_value = row.xpath('@class').extract()[0]
            classes = class_value.split(' ')
            if 'schedule_header' in classes:
                date_string = self._extract_text(row.css('.hc_date'))
                date = dateparser.parse(date_string).date()
            else:
                style = self._extract_text(row.css('span.classname'))
                style = re.sub(r' with .*', '', style)
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
                item['teacher'] = self._extract_text(row.css('span.trainer'))

                yield item
