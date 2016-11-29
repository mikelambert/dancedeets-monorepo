from .. import items

class EDGE(items.HealCodeScraper):
    name = 'EDGE'
    allowed_domains = ['www.edgepac.com']
    latlong = (34.0889302, -118.3310113)
    address = '6300 Romaine St, Suite 100, Los Angeles CA 90038'

    healcode_id = 'ca279668d92'

    def _valid_item(self, item, row):
        if not self._street_style(item['style']):
            return False
        if item['teacher'] == 'Class Cancelled':
            return False

        return True
