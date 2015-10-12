# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import urllib
import urllib2

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

def make_request(path, params):
    data = json.dumps(params)
    quoted_data = urllib.quote_plus(data)
    f = urllib2.urlopen('http://dev.dancedeets.com:8080/%s' % path, quoted_data)
    result = f.read()
    return result

class SaveStudioClassPipeline(object):

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        params = {
            'studio_name': spider.name,
        }
        print params
        result = make_request('classes/finish_upload', params)
        if result:
            print 'Upload returned: ', result

    def process_item(self, item, spider):
        new_item = dict(item)
        for key in ['start_time', 'end_time', 'scrape_time']:
            new_item[key] = new_item[key].strftime(DATETIME_FORMAT)
        new_item['auto_categories'] = [x.index_name for x in new_item['auto_categories']]
        result = make_request('classes/upload', new_item)
        if result:
            print 'Upload returned: ', result
