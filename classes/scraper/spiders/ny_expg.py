import dateparser
import datetime
from .. import items
from .. import mindbody_scraper

def parse_times(times):
    start, end = times.split(u' - ')
    return dateparser.parse('%s pm' % start).time(), dateparser.parse('%s pm' % end).time()

class EXPG(items.StudioScraper):
    name = 'EXPG'
    allowed_domains = ['expg-ny.com']
    latlong = (40.7246, -73.993123)
    address = '27 2nd Ave, New York, NY'

    start_urls = [
        'http://expg-ny.com/schedule.html',
    ]

    def parse_classes(self, response):
        table = response.css('div.schedule_container')
        for day_block in table.css('li.schedule_span'):
            day = day_block.css('.sdl_span_ttl').xpath('./text()').extract()[0]
            if day == 'CLASSES':
                continue
            date = dateparser.parse(day).date()
            for schedule_block in day_block.css('li.timetable_cell_wp'):
                times = schedule_block.css('.sdl_span_time').xpath('./text()').extract()[0]
                start_time, end_time = parse_times(times)
                for class_block in schedule_block.css('.timetable_cell'):
                    style_list = class_block.css('.cell_txt_cate').xpath('./text()')
                    if not style_list:
                        continue
                    style = style_list[0]
                    style = class_block.css('.cell_txt_cate').xpath('./text()').extract()[0]
                    level = class_block.css('.cell_txt_mbnone').xpath('./text()').extract()[0]
                    real_style = '%s %s' % (level, style)
                    
                    item = items.StudioClass()
                    item['start_time'] = datetime.datetime.combine(date, start_time)
                    item['end_time'] = datetime.datetime.combine(date, end_time)
                    item['style'] = real_style
                    item['teacher'] = self._extract_text(class_block.css('.cell_txt_pc')).title()
                    # This information is incorrect on their website :(
                    #teacher_link = class_block.css('.table_middle_tate').xpath('./a/@href').extract()[0]
                    #item['teacher_link'] = teacher_link
                    for new_item in self._repeated_items_iterator(item):
                        yield new_item
