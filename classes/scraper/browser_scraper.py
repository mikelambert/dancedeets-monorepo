import dateparser
import datetime
import re

import scrapy
import scrapyjs

import keys
from . import items


SERVER_URL = 'https://b54f18og-splash.scrapinghub.com'

# Or...to test this code locally, you must run a Splash server.
# Start a docker server running splash, as described here:
# http://splash.readthedocs.org/en/latest/install.html
# For Mac OS X, I ran Docker Quickstart Terminal, and then ran the command from the docs:
# $ docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 scrapinghub/splash
# Then configure the SERVER_URL to point at your local instance,
# in my case: 192.168.99.100
# SERVER_URL = 'http://192.168.99.100:8050'


def adjust_caps(s):
    if s.upper() == s:
        s = s.title()
    return s


class MindBodyBrowserScraper(items.StudioScraper):
    allowed_domains = ['clients.mindbodyonline.com']

    mindbody_studio_id = 0

    # So we can log in to our scrapinghub splash instance
    http_user = keys.get('scrapinghub_key')
    http_pass = ''

    custom_settings = {
        'SPLASH_URL': SERVER_URL,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapyjs.SplashMiddleware': 725,
        },
        'DUPEFILTER_CLASS': 'scrapyjs.SplashAwareDupeFilter',
        'HTTPCACHE_STORAGE': 'scrapyjs.SplashAwareFSCacheStorage',
        'ITEM_PIPELINES': {
            'classes.scraper.pipelines.BatchSaveStudioClassPipeline': 300,
        }
    }

    def __init__(self, *args, **kwargs):
        super(MindBodyBrowserScraper, self).__init__(*args, **kwargs)

    def start_requests(self):
        script = """
        function main(splash)
            assert(splash:go(splash.args.url))
            splash:wait(1)
            -- We need to click on the "CLASSES" tab.
            -- Unfortunately, attempts to call click() or evaljs onclick don't seem to work...
            -- So instead load the tab's URL directly in our main browser window
            splash:go("https://clients.mindbodyonline.com/classic/mainclass?fl=true&tabID=102")
            splash:wait(1)
            %s
            return splash:evaljs("document.getElementById('classSchedule-mainTable').outerHTML")
        end
        """

        # default week
        yield scrapy.Request(
            'https://clients.mindbodyonline.com/ASP/home.asp?studioid=%s' % self.mindbody_studio_id,
            meta={
                'splash': {
                    'args': {
                        'lua_source': script % "",
                    },
                    'endpoint': 'execute',
                    # optional parameters
                    'slot_policy': scrapyjs.SlotPolicy.PER_DOMAIN,
                }
            },
        )

        # week 2!
        yield scrapy.Request(
            'https://clients.mindbodyonline.com/ASP/home.asp?studioid=%s' % self.mindbody_studio_id,
            meta={
                'splash': {
                    'args': {
                        'lua_source': script % """
                            splash:runjs("document.getElementById('week-arrow-r').click()")
                            splash:wait(3)
                        """,
                    },
                    'endpoint': 'execute',
                    # optional parameters
                    'slot_policy': scrapyjs.SlotPolicy.PER_DOMAIN,
                }
            },
        )

    def _valid_item(self, item, row):
        return True

    def parse_classes(self, response):
        date = None
        for row in response.css('table#classSchedule-mainTable tr'):
            header = row.css('td.header')
            cells = row.css('td')
            if header:
                date = dateparser.parse(self._extract_text(header)).date()
            elif len(cells) == 6:
                item = items.StudioClass()
                lst = row.css('td')
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
