from .. import items

class Millenium(items.HealCodeScraper):
    name = 'Millenium'
    latlong = (34.1633887, -118.3763954)
    address = '5113 Lankershim Blvd., North Hollywood, CA 91601'

    healcode_id = '8113116c418'

    def _valid_item(self, item, row):
        class_types = self._extract_text(row.css('span.type_group'))
        if 'Adult Program' not in class_types:
            return False
        if not self._street_style(item['style']):
            return False
        return True
