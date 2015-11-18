import dateparser
import datetime
from .. import items

from nlp import event_classifier
from nlp import rules

def parse_times(time_string):
    start_string, end_string = time_string.split(' - ')
    start_time = dateparser.parse(start_string + ' pm').time()
    end_time = dateparser.parse(end_string).time()
    return start_time, end_time

class PMTHouseOfDance(items.StudioScraper):
    name = 'PMT'
    allowed_domains = ['pmthouseofdance.com']
    latlong = (40.7374272, -73.9987284)
    address = '69 W 14th St, New York, NY'

    start_urls = [
        'http://www.pmthouseofdance.com/?_escaped_fragment_=schedule/c1jfb',
    ]
    def _get_url(self, response):
        return 'http://www.pmthouseofdance.com/#!schedule/c1jfb'

    def parse_classes(self, response):
        table = response.css('div.Text')

        captured_columns = []
        rows_to_capture = 0
        for text_block in table:
            if 'Tuesday' in self._extract_text(text_block):
                rows_to_capture = 5
            if rows_to_capture > 0:
                cells = []
                for row in text_block.xpath('.//p'):
                    cells.append(self._extract_text(row.xpath('.')))
                captured_columns.append(cells)
            rows_to_capture -= 1

        row_by_row = zip(*captured_columns)

        day = None # Keep track of this row-to-row
        for row in row_by_row:
            if not row[1] or '---' in row[1]:
                continue
            potential_day = row[0]
            if potential_day:
                day = potential_day
                # Hack fix for broken PMT site
                if day == 'onday':
                    day = 'Monday'
                date = dateparser.parse(day).date()
            # Use our NLP event classification keywords to figure out which BDC classes to keep
            style = row[2]
            processor = event_classifier.StringProcessor(style)
            if not processor.has_token(rules.DANCE_STYLE):
                continue

            item = items.StudioClass()
            item['style'] = style
            item['teacher'] = row[3]
            # do we care?? row[4]
            start_time, end_time = parse_times(row[1])
            item['start_time'] = datetime.datetime.combine(date, start_time)
            item['end_time'] = datetime.datetime.combine(date, end_time)
            for new_item in self._repeated_items_iterator(item):
                yield new_item


