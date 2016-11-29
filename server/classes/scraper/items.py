# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import dateparser
import datetime
import logging
import re

import scrapy
from scrapy import item

from nlp import event_classifier
from nlp import categories
from nlp import keywords
from nlp import rules
from scrapy_lib import pipelines


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


class SaveStudioClassPipeline(pipelines.SaveToServerPipeline):
    server_path = 'classes/upload_multi'


class StudioScraper(scrapy.Spider):
    """Base class for all our studio scrapers. Does some per-item field setup that is common across studios."""

    _future_days = 14 # How many days of data to produce. Each iterator should check against this or self._future_horizon.

    custom_settings = {
        'ITEM_PIPELINES': {
            'classes.scraper.items.SaveStudioClassPipeline': 300,
        }
    }

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
        return StudioScraper._cleanup(' '.join(x.strip() for x in cell.xpath('.//text()').extract() if x.strip()).strip())

    def __init__(self, **kwargs):
        super(StudioScraper, self).__init__(**kwargs)
        self.scrape_time = datetime.datetime.now()

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
        class_text = re.sub(r'\b(?:[kj]\W?pop|pop up)\b', 'OTHER', class_text.lower())
        styles = categories.find_rules_in_text(class_text, categories.BROAD_STYLES)
        return styles

    def _get_url(self, response):
        return response.url

    def _future_horizon(self):
        return datetime.datetime.combine(datetime.date.today(), datetime.time.min) + datetime.timedelta(days=self._future_days)

    def _repeated_items_iterator(self, studio_class):
        """
        This is an iterator that produces two copies of a studio_class, a week apart.
        For use by subclasses that want to grab the correct datetimes for their studio_classes.
        """
        # If it's too old, wrap around one week
        if studio_class['start_time'].date() < datetime.date.today() - datetime.timedelta(days=1):
            studio_class['start_time'] += datetime.timedelta(days=7)
            studio_class['end_time'] += datetime.timedelta(days=7)
        while studio_class['start_time'] < self._future_horizon():
            yield studio_class.copy()
            # And always produce additional copies, a week at a time
            studio_class['start_time'] += datetime.timedelta(days=7)
            studio_class['end_time'] += datetime.timedelta(days=7)

    def _bogus_item(self, item):
        max_style = len('advanced intermediate hip hop with something else mixed in')
        max_teacher = len('someones longish-teacher and-last-name sub for crazy-long foreign-teacher different-name')
        if len(item['style']) > max_style or len(item['teacher']) > max_teacher:
            logging.error("Item contained too long properties: %s", item)
            return True
        return False

    def parse(self, response):
        for studio_class in self.parse_classes(response):
            if self._bogus_item(studio_class):
                continue
            if isinstance(studio_class, StudioClass):
                studio_class['teacher'] = self._cleanup(studio_class['teacher'])
                studio_class['style'] = self._cleanup(studio_class['style'])
                studio_class['source_page'] = self._get_url(response)
                studio_class['studio_name'] = self.name
                studio_class['recurrence_id'] = self._get_recurrence(studio_class)
                studio_class['auto_categories'] = self._get_auto_categories(studio_class)
                studio_class['scrape_time'] = self.scrape_time
                studio_class['latitude'] = self.latlong[0]
                studio_class['longitude'] = self.latlong[1]
                studio_class['address'] = self.address
                yield studio_class
            else:
                # Could be a regular Request object for nested scraping
                yield studio_class


class HealCodeScraper(StudioScraper):
    allowed_domains = ['healcode.com']

    healcode_id = '8113116c418'

    def __init__(self, *args, **kwargs):
        super(HealCodeScraper, self).__init__(*args, **kwargs)
        self.start_urls = [
            'https://widgets.healcode.com/widgets/schedules/print/%s' % self.healcode_id,
        ]

    def _valid_item(self, item, row):
        return True

    def parse_classes(self, response):
        table = response.css('table.schedule')
        for row in table.xpath('.//tr'):
            class_value = row.xpath('@class').extract()[0]
            classes = class_value.split(' ')
            if 'schedule_header' in classes:
                date_string = self._extract_text(row.css('.hc_date'))
                date = dateparser.parse(date_string).date()
            elif 'no_classes' in classes:
                pass
            else:
                item = StudioClass()
                start_time_str = row.css('.hc_starttime::text').extract()[0]
                end_time_str = row.css('.hc_endtime::text').extract()[0].replace(' - ', '')
                start_time = dateparser.parse(start_time_str).time()
                end_time = dateparser.parse(end_time_str).time()
                item['start_time'] = datetime.datetime.combine(date, start_time)
                item['end_time'] = datetime.datetime.combine(date, end_time)
                item['style'] = self._extract_text(row.css('span.classname'))
                item['teacher'] = self._extract_text(row.css('span.trainer'))

                if self._valid_item(item, row):
                    yield item
