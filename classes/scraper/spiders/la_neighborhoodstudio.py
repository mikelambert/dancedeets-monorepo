import re

from .. import items

class NeighborhoodStudio(items.HealCodeScraper):
    name = 'NeighborhoodStudio'
    latlong = (34.0237478, -118.384045)
    address = '3625 Hayden Ave, Culver City, CA 90232'

    healcode_id = '2961706fc'

    def _valid_item(self, item, row):
        item['style'] = re.sub(r' with .*', '', item['style'])
        if not self._street_style(item['style']):
            return False
        return True
