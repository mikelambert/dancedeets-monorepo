import logging
import urlparse

import scrapy
import scrapyjs
from scrapy.linkextractors import LinkExtractor

from scrapy_lib import mixins
from .. import fbitems


def split_list_on_element(lst, split_elem):
    new_list = ['']
    for elem in lst:
        if split_elem(elem):
            new_list.append('')
        else:
            new_list[-1] += elem
    return [x.strip() for x in new_list]


class BBoyBattlesScraper(mixins.BrowserScraperMixin, fbitems.FbEventScraper):
    name = 'BBoyBattles'
    allowed_domains = ['bboybattles.org']

    custom_settings = mixins.generate_custom_settings(
        fbitems.FbEventScraper.custom_settings
    )

    def _generate_request(self, url):
        script = """
        function main(splash)
            assert(splash:go(splash.args.url))
            return splash:evaljs("document.body.outerHTML")
        end
        """
        return scrapy.Request(
            url,
            meta={
                'splash': {
                    'args': {
                        'lua_source': script,
                    },
                    'endpoint': 'execute',
                    # optional parameters
                    'slot_policy': scrapyjs.SlotPolicy.PER_DOMAIN,
                }
            },
        )

    def start_requests(self):
        yield self._generate_request('http://www.bboybattles.org/Battles.aspx')

    def parse(self, response):
        e = LinkExtractor()
        urls = [link.url for link in e.extract_links(response)]
        for url in urls:
            parsed = urlparse.urlsplit(url)
            qs = urlparse.parse_qs(parsed.query)
            if qs and 'Url' in qs:
                event_url = qs['Url']
                yield fbitems.AddFacebookEvent(event_url)
