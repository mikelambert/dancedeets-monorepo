# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
import urllib
import urllib2


from classes import class_forms
from wtforms.compat import iteritems

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
        form = class_forms.ClassForm(data=item)
        form_dict = dict((name, f._value()) for name, f in iteritems(form._fields))
        f = urllib2.urlopen('http://dev.dancedeets.com:8080/classes/upload', urllib.urlencode(form_dict))
        print f.read()

        return item
