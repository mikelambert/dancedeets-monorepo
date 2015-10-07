# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from nlp import categories

class StudioClass(scrapy.DictItem):
    """This is basically a dictionary with methods.
    Originally was using scrapy.Item and scrapy.ItemLoader,
    but it was making the code more complex than necessary.

    This is a more straightforward API that removes a bunch of the magic.
    """

    # We could get rid of the need for this by subclassing scrapy.BaseItem.
    # But this provides some element of safety by enforcing field names.
    fields = [
        'studio',
        'source_page',
        'recurrence_id',
        'style',
        'teacher',
        'teacher_link',
        'start_time',
        'end_time',
        'auto_categories'
    ]

    def add(self, field, selected):
        self[field] = ' '.join(x.strip() for x in selected.extract() if x.strip())

class StudioScraper(scrapy.Spider):
    """Base class for all our studio scrapers. Does some per-item field setup that is common across studios."""

    def parse_classes(self, response):
        raise NotImplementedError()

    def _get_recurrence(self, item):
        """Returns a recurrence_id using fields that remain stable week-to-week,
        and also uniquely identify a class recurrance."""
        start_time_string = item['start_time'].strftime('Day %w: %H:%M')
        return '%s: %s: %s' % (item['studio'], start_time_string, item['style'])

    def _get_auto_categories(self, item):
        """Parses the fields we have and returns a list of categories for indexing.
        Should have a list of styles, plus a class."""
        class_text = '%s: %s' % (item['style'], item['teacher'])
        styles = categories.find_rules_in_text(class_text, categories.BROAD_STYLES)
        return styles

    def parse(self, response):
        for item in self.parse_classes(response):
            item['source_page'] = response.url
            item['studio'] = self.name
            item['recurrence_id'] = self._get_recurrence(item)
            item['auto_categories'] = self._get_auto_categories(item)
            yield item
