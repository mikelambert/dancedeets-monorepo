from .. import browser_scraper


class Quest(browser_scraper.MindBodyBrowserScraper):
    name = 'Quest'
    latlong = (33.8727865, -118.079369)
    address = '11976 Artesia Blvd, Artesia CA'

    mindbody_studio_id = 110557
    mindbody_tab_id = 7

    def _valid_item(self, item, row):
        return self._street_style(item['style'])
