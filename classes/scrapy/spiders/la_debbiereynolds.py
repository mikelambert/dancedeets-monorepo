import dateparser
import datetime
import re
import urlparse

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

class DebbieReynolds(items.StudioScraper):
    name = 'DebbieReynolds'
    allowed_domains = ['www.drdancestudio.com']
    latlong = (34.188804, -118.3895947)
    address = '6514 Lankershim Blvd., North Hollywood, CA 91606'

    start_urls = [
        'http://www.drdancestudio.com/schedule',
    ]

    def parse_classes(self, response):
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day_block in enumerate(response.css('div.view-schedule')):
            schedule_block = day_block.css('table.views-table')
            date = dateparser.parse(days[i]).date()
            if date < datetime.date.today():
                date += datetime.timedelta(days=7)
            for class_block in schedule_block.css('tr'):
                cells = class_block.xpath('td')
                cells = [' '.join(x.xpath('.//text()').extract()).strip() for x in cells]
                times, style, level, instructor, sub, editnode = cells
                full_style = '%s %s' % (level, style)
                if not self._street_style(full_style):
                    continue

                start_time, end_time = parse_times(times)

                item = items.StudioClass()
                item['start_time'] = datetime.datetime.combine(date, start_time)
                item['end_time'] = datetime.datetime.combine(date, end_time)
                item['style'] = full_style
                item['teacher'] = instructor
                # This information is incorrect on their website :(
                teacher_link = class_block.css('.views-field-field-class-inst').xpath('./a/@href').extract()[0]
                url = urlparse.urljoin(response.url, teacher_link)
                item['teacher_link'] = url
                yield item
