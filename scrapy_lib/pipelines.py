# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
import json
import keys
import logging
import urllib
import urllib2

DATETIME_FORMAT_TZ = "%Y-%m-%dT%H:%M:%S%z"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

PROD_SERVER = 'www.dancedeets.com'
DEV_SERVER = 'dev.dancedeets.com:8080'


def make_request(server, path, params):
    new_params = params.copy()
    new_params['scrapinghub_key'] = keys.get('scrapinghub_key')
    data = json.dumps(new_params)
    quoted_data = urllib.quote_plus(data)
    f = urllib2.urlopen('http://%s/%s' % (server, path), quoted_data)
    result = f.read()
    return result


def make_requests(path, params):
    result = None
    try:
        result = make_request(PROD_SERVER, path, params)
    except urllib2.URLError as e:
        result = {'Error': e.reason}
        pass
    dev_result = None
    try:
        dev_result = make_request(DEV_SERVER, path, params)
    except urllib2.URLError as e:
        dev_result = {'Error': e.reason}
    return {'prod_result': result, 'dev_result': dev_result}


class SaveToServerPipeline(object):
    server_path = None
    batch_size = None

    def open_spider(self, spider):
        assert self.server_path, "Must set the server_path member variable."
        self.items = []
        pass

    def close_spider(self, spider):
        self.send_batch(spider)

    def send_batch(self, spider):
        logging.info('Sending batch of %s items', len(self.items))
        params = {
            'studio_name': spider.name,
            'items': self.items,
        }
        result = make_requests(self.server_path, params)
        self.items = []
        if result:
            logging.info('Upload returned: %s', result)

    def process_item(self, item, spider):
        new_item = dict(item)
        for key in ['start_time', 'end_time', 'scrape_time']:
            if new_item.get(key):
                dt = new_item[key]
                if isinstance(dt, datetime.datetime) and dt.tzinfo:
                    new_item[key] = dt.strftime(DATETIME_FORMAT_TZ)
                else:
                    new_item[key] = dt.strftime(DATETIME_FORMAT)
        if 'auto_categories' in new_item:
            new_item['auto_categories'] = [x.index_name for x in new_item['auto_categories']]
        self.items.append(new_item)
        if self.batch_size and len(self.items) >= self.batch_size:
            self.send_batch(spider)
        return new_item


class SaveEventsToServerPipeline(object):
    server_path = None
    batch_size = None

    def open_spider(self, spider):
        assert self.server_path, "Must set the server_path member variable."
        self.items = []
        pass

    def close_spider(self, spider):
        self.send_batch(spider)

    def send_batch(self, spider):
        logging.info('Sending batch of %s items', len(self.items))
        params = {
            'events': self.items,
        }
        result = make_requests(self.server_path, params)
        self.items = []
        if result:
            logging.info('Upload returned: %s', result)

    def process_item(self, item, spider):
        self.items.append(item['url'])
        if self.batch_size and len(self.items) >= self.batch_size:
            self.send_batch(spider)
        return item
