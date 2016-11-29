import dateparser
import datetime
import re
import urllib

import scrapy
import scrapyjs

from . import items
from scrapy_lib import mixins

def adjust_caps(s):
    if s.upper() == s:
        s = s.title()
    return s


class BrowserScraper(items.StudioScraper, mixins.BrowserScraperMixin):
    custom_settings = mixins.generate_custom_settings(
        items.StudioScraper.custom_settings
    )



class MindBodyBrowserScraper(BrowserScraper):
    allowed_domains = ['clients.mindbodyonline.com']

    mindbody_studio_id = 0
    mindbody_tab_id = 0

    def _main_mindbody_url(self):
        return 'https://clients.mindbodyonline.com/ASP/home.asp?studioid=%s' % self.mindbody_studio_id

    def _generate_request(self, post_load=''):
        script = """
        function main(splash)
            assert(splash:go(splash.args.url))
            splash:wait(1)
            -- We need to click on the "CLASSES" tab.
            -- Unfortunately, attempts to call click() or evaljs onclick don't seem to work...
            -- So instead load the tab's URL directly in our main browser window
            splash:go("https://clients.mindbodyonline.com/classic/mainclass?fl=true&%s")
            splash:wait(1)
            %s
            return splash:evaljs("document.getElementById('classSchedule-mainTable').outerHTML")
        end
        """
        url_args = urllib.urlencode({'tabID': self.mindbody_tab_id})
        return scrapy.Request(
            self._main_mindbody_url(),
            meta={
                'splash': {
                    'args': {
                        'lua_source': script % (url_args, post_load),
                    },
                    'endpoint': 'execute',
                    # optional parameters
                    'slot_policy': scrapyjs.SlotPolicy.PER_DOMAIN,
                }
            },
        )

    def _get_url(self, response):
        return self._main_mindbody_url()

    def start_requests(self):
        yield self._generate_request()
        yield self._generate_request("""
            splash:runjs("autoSubmitDateTo(false, true)")
            splash:wait(3)
        """)

    def _valid_item(self, item, row):
        return True

    def parse_classes(self, response):
        date = None
        for row in response.css('table#classSchedule-mainTable tr'):
            header = row.css('td.header')
            cells = row.css('td')
            if header:
                date = dateparser.parse(self._extract_text(header)).date()
            elif len(cells) in [5, 6]:
                item = items.StudioClass()
                lst = row.css('td')
                if len(lst) == 5:
                    start_time, dummy, class_name, teacher, duration = [self._extract_text(x) for x in lst]
                elif len(lst) == 6:
                    start_time, dummy, class_name, teacher, room, duration = [self._extract_text(x) for x in lst]
                if 'Cancelled' in teacher:
                    continue
                start_time = dateparser.parse(start_time).time()
                duration_hours_match = re.search('(\d+) hour', duration)
                duration_hours = duration_hours_match.group(1) if duration_hours_match else 0
                duration_minutes_match = re.search('(\d+) minute', duration)
                duration_minutes = duration_minutes_match.group(1) if duration_minutes_match else 0
                duration = datetime.timedelta(hours=int(duration_hours), minutes=int(duration_minutes))
                item['start_time'] = datetime.datetime.combine(date, start_time)
                item['end_time'] = datetime.datetime.combine(date, start_time) + duration
                item['style'] = class_name
                if ' for ' in teacher:
                    sub, orig = teacher.split(' for ')
                    sub = adjust_caps(sub)
                    orig = adjust_caps(orig)
                    teacher = '%s for %s' % (sub, orig)
                teacher = adjust_caps(teacher)
                item['teacher'] = teacher
                if self._valid_item(item, row):
                    yield item
