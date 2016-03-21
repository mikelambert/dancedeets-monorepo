# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import logging
import re

import html2text
import scrapy
from scrapy import item

from nlp import event_classifier
from nlp import keywords
from nlp import rules
from scrapers import pipelines


class WebEvent(item.DictItem):
    """This is basically a dictionary with methods.
    Originally was using scrapy.Item and scrapy.ItemLoader,
    but it was making the code more complex than necessary.

    This is a more straightforward API that removes a bunch of the magic.
    """

    # We could get rid of the need for this by subclassing scrapy.BaseItem.
    # But this provides some element of safety by enforcing field names.
    fields = [
        'id',
        'website',
        'title',
        'description',
        'photo',
        'starttime',
        'endtime',
        'location_name',
        'location_address',
        'latitude',
        'longitude',
    ]


class AddFacebookEvent(item.BaseItem):
    def __init__(self, url):
        self.fb_url = url

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.fb_url)


def _extract_text(cell):
    return _format_text(' '.join(cell.extract()))


def _format_text(html):
    text = re.sub(' +\n', '\n', html2text.html2text(html, bodywidth=0).replace('\n\n', '\n')).strip()
    # If we have too many header lines, strip them out (bad html formatter that does <h1> on everything)
    lines = text.count('\n')
    header_lines = len(re.findall(r'^# ', text, re.MULTILINE))
    if header_lines > lines / 8:
        text = re.sub('\n# ', '', text)
    return text


def get_line_after(text, regex):
    desc_lines = text.split('\n')
    return_next_line = False
    for line in desc_lines:
        if return_next_line:
            if line:
                return line
        if re.search(regex, line):
            after_keyword = re.split(regex, line, 1)[1]
            # If it's a "keyword: something"...return the same line
            if len(after_keyword) > 4:
                return after_keyword.replace(u'：', '').strip()
            return_next_line = True
    return None


class SaveWebEventPipeline(pipelines.BatchSaveToServerPipeline):
    server_path = 'web_events/upload_multi'


class WebEventScraper(scrapy.Spider):
    """Base class for all our web event scrapers. Does some per-item field setup that is common across web events."""

    _future_days = 14 # How many days of data to produce. Each iterator should check against this or self._future_horizon.

    custom_settings = {
        'ITEM_PIPELINES': {
            'web_events.scraper.items.SaveWebEventPipeline': 300,
        }
    }

    @staticmethod
    def _street_style(style):
        # Use our NLP event classifition keywords to figure out which BDC classes to keep
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
        return _extract_text(cell)

    def _get_recurrence(self, studio_class):
        """Returns a recurrence_id using fields that remain stable week-to-week,
        and also uniquely identify a class recurrance."""
        start_time_string = studio_class['start_time'].strftime('Day %w: %H:%M')
        return '%s: %s: %s' % (studio_class['studio_name'], start_time_string, studio_class['style'])

    def _get_url(self, response):
        return response.url

    def _bogus_item(self, item):
        max_style = len('advanced intermediate hip hop with something else mixed in')
        max_teacher = len('someones longish-teacher and-last-name sub for crazy-long foreign-teacher different-name')
        if len(item['style']) > max_style or len(item['teacher']) > max_teacher:
            logging.error("Item contained too long properties: %s", item)
            return True
        return False

"""
    def parse(self, response):
        scrape_time = datetime.datetime.now()
        for item in self.parse_classes(response):
            if self._bogus_item(item):
                continue
            if isinstance(item, WebEvent):
                yield item
            else:
                # Could be a regular Request object for nested scraping
                yield item
"""
