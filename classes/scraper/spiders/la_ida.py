import dateparser

from .. import browser_scraper


def parse_times(times):
    start, end = times.split(u' - ')
    return dateparser.parse(start).time(), dateparser.parse(end).time()


class IDA(browser_scraper.MindBodyBrowserScraper):
    name = 'IDA'
    latlong = (34.1019203, -118.339862)
    address = '6755 Hollywood Blvd., Suite 200 Los Angeles, CA 90028'

    # healcode_id = '622563634f1'

    mindbody_studio_id = 6131
    mindbody_tab_id = 7

    def _valid_item(self, item, row):
        if not self._street_style(item['style']):
            return False
        return True
