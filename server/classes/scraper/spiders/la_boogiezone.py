from .. import browser_scraper


class Boogiezone(browser_scraper.MindBodyBrowserScraper):
    name = 'Boogiezone'
    latlong = (33.831684, -118.3177987)
    address = '1951 Carson Street, Torrance, CA 90501'

    mindbody_studio_id = 350
    mindbody_tab_id = 7

    def _valid_item(self, item, row):
        if not self._street_style(item['style']):
            return False
        if item['teacher'] == 'Cancelled Today':
            return False

        return True
