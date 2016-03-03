import dateparser
import datetime
import urlparse

from .. import items


def parse_times(times):
    start, end = times.split(u' - ')
    return dateparser.parse(start).time(), dateparser.parse(end).time()


class IDA(items.HealCodeScraper):
    name = 'IDA'
    allowed_domains = ['www.idahollywood.com']
    latlong = (34.1019203, -118.339862)
    address = '6755 Hollywood Blvd., Suite 200 Los Angeles, CA 90028'

    healcode_id = '622563634f1'

    def _valid_item(self, item, row):
        if not self._street_style(item['style']):
            return False
        return True
