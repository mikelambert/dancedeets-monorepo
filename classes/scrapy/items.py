# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import loader
from scrapy.loader import processors
import string

class ClassItem(scrapy.Item):
    studio = scrapy.Field()
    style = scrapy.Field()
    teacher = scrapy.Field()
    teacher_link = scrapy.Field()
    start_time = scrapy.Field()
    end_time = scrapy.Field()

StripAndCombine = processors.Compose(processors.MapCompose(string.strip), processors.Join(' '), processors.MapCompose(string.strip))
class ClassLoader(loader.ItemLoader):
    teacher_in = StripAndCombine
    style_in = StripAndCombine
