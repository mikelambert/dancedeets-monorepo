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
        new_item = dict(item)
        new_item['start_time'] = new_item['start_time'].strftime(DATETIME_FORMAT)
        new_item['end_time'] = new_item['end_time'].strftime(DATETIME_FORMAT)
        new_item['auto_categories'] = [x.index_name for x in new_item['auto_categories']]
        data = json.dumps(new_item)
        quoted_data = urllib.quote_plus(data)
        f = urllib2.urlopen('http://dev.dancedeets.com:8080/classes/upload', quoted_data)
        result = f.read()
        if result:
            print 'Upload returned: ', result
