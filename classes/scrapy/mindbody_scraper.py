#!/usr/bin/env python

import datetime
import logging

from classes.scrapy import items
import mindbody

# Before we can use this Scraper on a MindBody site, we must first get the admin to open:
# mindbody.get_activation_link(-99)

# scrapy sets verbose logging by default, but we don't want to see suds spam.
logger = logging.getLogger('suds')
logger.setLevel(logging.INFO)

SPONSOR_MINDBODY = 'MINDBODY'

class MindBodyScraper(items.StudioScraper):
    site_id = -99
    filter_style = False

    start_urls = ['https://www.google.com']

    def _get_url(self, response):
        return 'https://clients.mindbodyonline.com/ASP/home.asp?studioid=%s' % self.site_id

    def parse_classes(self, response):
        start = datetime.datetime.combine(datetime.date.today(), datetime.time())
        end = start + datetime.timedelta(days=14)

        # Temporarily disable DEBUG logging, suds is too verbose
        #logging.root.setLevel(logging.INFO)
        result = mindbody.get_classes(start_time=start, end_time=end, hide_canceled_classes=True, site_id=self.site_id)
        #logging.root.setLevel(logging.NOTSET)

        if result.Status != 'Success':
            raise IOError("MindBody gave result: %s: %s" % (result.Status, result.Message))
        if result.TotalPageCount != 1:
            raise IOError("Too many results for our query, got %s pages of data back" % result.TotalPageCount)

        for studio_class in result.Classes.Class:
            self.address = '%s, %s' % (studio_class.Location.Address, studio_class.Location.Address2)
            self.latlong = (studio_class.Location.Latitude, studio_class.Location.Longitude)
            self.name = studio_class.Location.Name

            style = studio_class.ClassDescription.Name
            if self.filter_style:
                if not self._street_style(style):
                    continue

            item = items.StudioClass()
            item['style'] = style
            item['start_time'] = studio_class.StartDateTime
            item['end_time'] = studio_class.EndDateTime
            item['teacher'] = studio_class.Staff.Name
            item['sponsor'] = SPONSOR_MINDBODY
            yield item
