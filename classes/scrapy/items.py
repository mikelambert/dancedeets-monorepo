# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import loader
from scrapy.loader import processors
import string

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

    def _get_recurrence(self):
        """Returns a recurrence_id using fields that remain stable week-to-week,
        and also uniquely identify a class recurrance."""
        start_time_string = self['start_time'].strftime('Day %w: %H:%M')
        return '%s: %s: %s' % (self['studio'], start_time_string, self['style'])

    def _get_auto_categories(self):
        """Parses the fields we have and returns a list of categories for indexing.
        Should have a list of styles, plus a class."""
        class_text = '%s: %s' % (self['style'], self['teacher'])
        styles = categories.find_rules_in_text(class_text, categories.BROAD_STYLES)
        return styles

    def polish(self):
        self['title']
        if 'recurrence_id' not in self:
            self['recurrence_id'] = self._get_recurrence()
        if 'auto_categories' not in self:
            self['auto_categories'] = self._get_auto_categories()
        return self

    def set_selected(self, field, selected):
        self[field] = ' '.join(x.strip() for x in selected.extract() if x.strip())

