# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import datetime
import re

import scrapy
from scrapy import item

from nlp import event_classifier
from nlp import categories
from nlp import keywords
from nlp import rules

class StudioClass(item.DictItem):
    """This is basically a dictionary with methods.
    Originally was using scrapy.Item and scrapy.ItemLoader,
    but it was making the code more complex than necessary.

    This is a more straightforward API that removes a bunch of the magic.
    """

    # We could get rid of the need for this by subclassing scrapy.BaseItem.
    # But this provides some element of safety by enforcing field names.
    fields = [
        'studio_name',
        'source_page',
        'recurrence_id',
        'style',
        'teacher',
        'teacher_link',
        'start_time',
        'end_time',
        'auto_categories',
        'scrape_time',
        'latitude',
        'longitude',
        'address',
        'sponsor',
    ]

class StudioScraper(scrapy.Spider):
    """Base class for all our studio scrapers. Does some per-item field setup that is common across studios."""

    #def __init__(self, *args, **kwargs):
    #    super(StudioScraper, self).__init__(self, *args, **kwargs)

    @staticmethod
    def _street_style(style):
        # Use our NLP event classification keywords to figure out which BDC classes to keep
        processor = event_classifier.StringProcessor(style)
        # Get rid of "Ballet with Pop Music"
        processor.real_tokenize(keywords.PREPROCESS_REMOVAL)
        return processor.has_token(rules.DANCE_STYLE)

    @staticmethod
    def _cleanup(s):
        result = re.sub(r'\s', ' ', s).replace(u'\xa0', ' ')
        return result

    @staticmethod
    def _extract_text(cell):
        return ' '.join(x.strip() for x in cell.xpath('.//text()').extract() if x.strip()).strip()

    def parse_classes(self, response):
        raise NotImplementedError()

    def _get_recurrence(self, studio_class):
        """Returns a recurrence_id using fields that remain stable week-to-week,
        and also uniquely identify a class recurrance."""
        start_time_string = studio_class['start_time'].strftime('Day %w: %H:%M')
        return '%s: %s: %s' % (studio_class['studio_name'], start_time_string, studio_class['style'])

    def _get_auto_categories(self, studio_class):
        """Parses the fields we have and returns a list of categories for indexing.
        Should have a list of styles, plus a class."""
        class_text = '%s: %s' % (studio_class['style'], studio_class['teacher'])
        styles = categories.find_rules_in_text(class_text, categories.BROAD_STYLES)
        return styles

    def _get_url(self, response):
        return response.url

    def parse(self, response):
        scrape_time = datetime.datetime.now()
        for studio_class in self.parse_classes(response):
            if isinstance(studio_class, StudioClass):
                studio_class['teacher'] = self._cleanup(studio_class['teacher'])
                studio_class['style'] = self._cleanup(studio_class['style'])
                studio_class['source_page'] = self._get_url(response)
                studio_class['studio_name'] = self.name
                studio_class['recurrence_id'] = self._get_recurrence(studio_class)
                studio_class['auto_categories'] = self._get_auto_categories(studio_class)
                studio_class['scrape_time'] = scrape_time
                studio_class['latitude'] = self.latlong[0]
                studio_class['longitude'] = self.latlong[1]
                studio_class['address'] = self.address
                yield studio_class
            else:
                # Could be a regular Request object for nested scraping
                yield studio_class
