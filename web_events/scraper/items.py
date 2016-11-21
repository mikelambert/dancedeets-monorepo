# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import logging
import re
import urlparse

import html2text
import HTMLParser
import scrapy
from scrapy import item

from nlp import event_classifier
from nlp import keywords
from nlp import rules
from scrapy_lib import pipelines
from util import strip_markdown


class WebEvent(item.DictItem):
    """This is basically a dictionary with methods.
    Originally was using scrapy.Item and scrapy.ItemLoader,
    but it was making the code more complex than necessary.

    This is a more straightforward API that removes a bunch of the magic.
    """

    # We could get rid of the need for this by subclassing scrapy.BaseItem.
    # But this provides some element of safety by enforcing field names.
    fields = [
        'namespace',
        'namespaced_id',
        'name',
        'description',
        'photo',
        'start_time',
        'end_time',
        'location_name',
        'location_address',
        'geolocate_location_name', # used to geolocate this event
        'latitude',
        'longitude',
    ]


class AddFacebookEvent(item.BaseItem):
    def __init__(self, url):
        self.fb_url = url

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.fb_url)


def extract_text(cell):
    return format_text(' '.join(cell.extract()))


def format_text(html):
    text = html2text.html2text(html, bodywidth=0).replace('\n\n', '\n')
    text = HTMLParser.HTMLParser().unescape(text)
    text = strip_markdown.strip(text)
    text = re.sub(' +\n', '\n', text).strip()
    text = re.sub('\n\n\n', '\n\n', text)
    return text


def get_line_after(text, regex):
    desc_lines = text.split('\n')
    return_next_line = False
    for line in desc_lines:
        if return_next_line and line.strip():
            value = line.strip()
            value = re.sub(ur'[＠@]', '', value)
            paren_re = ur'[(（]'
            if re.search(paren_re, value):
                value = re.split(paren_re, value, 1)[0]
            return value
        if re.search(regex, line):
            prefix, value = re.split(regex, line, 1)
            # If it's part of a longish text like this, ignore:
            # ＊HIPHOP&HOUSEエントリー者は11:30までに会場集合
            if len(prefix) > 3:
                continue
            colon_re = ur'[：:】]'
            # If it's a "keyword: something"...return the same line
            if re.search(colon_re, value):
                value = re.split(colon_re, value, 1)[1]
            elif re.search(r'\s', value):
                # Or if it's a 【会場】 HARLEM, grab everything after the first space
                value = re.split(r'\s', value, 1)[1]
            value = value.strip()
            if len(value) > 2:
                return value
            return_next_line = True
    return None


class SaveWebEventPipeline(pipelines.SaveToServerPipeline):
    server_path = 'web_events/upload_multi'
    batch_size = 20


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

    def base_url(self, response):
        base_href = response.xpath('//base[@href]/@href')
        if base_href:
            return base_href.extract()[0]
        else:
            return response.url

    def abs_url(self, response, url):
        return urlparse.urljoin(self.base_url(response), url)

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
