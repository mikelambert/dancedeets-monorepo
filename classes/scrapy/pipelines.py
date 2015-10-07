# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
import json
import urllib
import urllib2

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

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
        new_item = item.copy()
        new_item['start_time'] = item['start_time'].strftime(DATETIME_FORMAT)
        new_item['end_time'] = item['end_time'].strftime(DATETIME_FORMAT)
        data = json.dumps(new_item)
        f = urllib2.urlopen('http://dev.dancedeets.com:8080/classes/upload', urllib.quote(data))
        print f.read()
