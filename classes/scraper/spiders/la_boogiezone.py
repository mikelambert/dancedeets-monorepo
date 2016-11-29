from .. import items

class Boogiezone(items.HealCodeScraper):
    name = 'Boogiezone'
    latlong = (33.831684, -118.3177987)
    address = '1951 Carson Street, Torrance, CA 90501'

    healcode_id = 'd914316d8e3'

    def _valid_item(self, item, row):
        if not self._street_style(item['style']):
            return False
        if item['teacher'] == 'Class Cancelled':
            return False

        return True
