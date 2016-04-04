import re

from .. import browser_scraper

class NeighborhoodStudio(browser_scraper.MindBodyBrowserScraper):
    name = 'NeighborhoodStudio'
    latlong = (34.0237478, -118.384045)
    address = '3625 Hayden Ave, Culver City, CA 90232'

    # healcode_id = '2961706fc'

    mindbody_studio_id = 14144
    mindbody_tab_id = 7

    def _valid_item(self, item, row):
        item['style'] = re.sub(r' with .*', '', item['style'])
        if not self._street_style(item['style']):
            return False
        return True
