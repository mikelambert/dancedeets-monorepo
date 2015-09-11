# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime

from classes import models

class SaveStudioClassPipeline(object):


    def open_spider(self, spider):
        self.scrape_time = datetime.datetime.now()

    def close_spider(self, spider):
        pass
        #TODO:
        #studio = XXX
        #studio.last_scrape_time = self.scrape_time
        #studio.put()

    def process_item(self, item, spider):
        studio_class = models.StudioClass()
        studio_class.studio_name = spider.name
        studio_class.source_page = item.source_page
        studio_class.style = item.style
        studio_class.teacher = item.teacher
        studio_class.teacher_link = item.teacher_link
        studio_class.start_time = item.start_time
        studio_class.end_time = item.end_time
        studio_class.scrape_time = self.scrape_time
        studio_class.put()

        return item
