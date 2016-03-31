import re

import event_types
from .. import browser_scraper


class MovementLifestyle(browser_scraper.MindBodyBrowserScraper):
    name = 'mL'
    latlong = (34.1673552, -118.3726311)
    address = '11105 Weddington St, North Hollywood, CA'

    mindbody_studio_id = 133521
    mindbody_tab_id = 7

    def _get_auto_categories(self, studio_class):
        categories = super(MovementLifestyle, self)._get_auto_categories(studio_class)
        lower_style = studio_class['style'].lower()
        if re.search(r'\b(?:class|ml)\b', lower_style):
            categories.append(event_types.HIPHOP)
        return list(set(categories))
