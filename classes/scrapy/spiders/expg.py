import dateparser
import datetime
import scrapy
from .. import items


def parse_times(times):
    start, end = times.split(u' - ')
    return dateparser.parse('%s pm' % start).time(), dateparser.parse('%s pm' % end).time()

class EXPG(scrapy.Spider):
    name = 'EXPG'
    allowed_domains = ['expg-ny.com']
    start_urls = [
        'http://expg-ny.com/schedule.html',
    ]

    def parse(self, response):
        table = response.css('div.schedule_container')
        for day_block in table.css('li.schedule_span'):
            day = day_block.css('.sdl_span_ttl').xpath('./text()').extract()[0]
            date = dateparser.parse(day)
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
                    
                    l = items.ClassLoader(item=items.ClassItem(), selector=class_block)
                    l.add_value('source_page', response.url)
                    l.add_value('start_time', datetime.datetime.combine(date, start_time))
                    l.add_value('end_time', datetime.datetime.combine(date, end_time))
                    l.add_value('style', real_style)
                    l.add_css('teacher', '.cell_txt_pc::text')
                    # This information is incorrect on their website :(
                    #teacher_link = class_block.css('.table_middle_tate').xpath('./a/@href').extract()[0]
                    #l.add_value('teacher_link', teacher_link)
                    yield l.load_item()
