# -*-*- encoding: utf-8 -*-*-

import datetime
from dateutil import relativedelta
import logging
import re
import urllib
import urlparse

import scrapy

from events import namespaces
from util import korean_dates
from util import strip_markdown
from .. import items


def split_list_on_element(lst, split_elem):
    new_list = ['']
    for elem in lst:
        if split_elem(elem):
            new_list.append('')
        else:
            new_list[-1] += elem
    return [x.strip() for x in new_list]


class StreetDanceKoreaScraper(items.WebEventScraper):
    name = 'StreetDanceKorea'
    allowed_domains = ['www.streetdancekorea.com']
    namespace = namespaces.KOREA_SDK

    def start_requests(self):
        today = datetime.date.today()
        # Query for next six months of events
        for i in range(6):
            d = today + relativedelta.relativedelta(months=i)
            yield scrapy.Request('http://www.streetdancekorea.com/Event/MainListGetMore.aspx?page=1&bid=Event&ge=&et=&od=&kw=&year=%s&month=%s' % (d.year, d.month))

    def _validate(self, split_on_br_nodes):
        """
        [
            u'<h3>Waack To The Beat vol.4</h3>',
            u'D-DAY -2 \uc77c',
            u'2016\ub144 3\uc6d4 12\uc77c(\ud1a0)',
            '',
            u'\uc7a5\ub974 : WAACKING',
            u'\uc774\ubca4\ud2b8 \ud0c0\uc785 : BATTLE',
            '',
            # ...
            u'\uc800\ubc88\ud589\uc0ac\ubcf4\ub2e4 \uc7ac\ubc0c\ub294 \ubc30\ud2c0\ub8f0\uc774 \ucd94\uac00\ub418\uc5c8\uc2b5\ub2c8\ub2e4',
            u'\uc880 \ub354 \uc5c5\uadf8\ub808\uc774\ub4dc\ub41c \uc880\ub354 \uc0c8\ub85c\uc6cc\uc9c4 WAACK TO THE BEAT vol.4 \ub9ce\uc740 \uae30\ub300\uc640 \uad00\uc2ec \ubd80\ud0c1\ub4dc\ub9bd\ub2c8\ub2e4',
            u'\uc800\ud76c \ub2ed\ucee4\ub4e4\uc758 \uba4b\uc9c4\ubb34\ube59 \uae30\ub300\ud558\uaca0\uc2b5\ub2c8\ub2e4',
        ]
        """
        if '<h3>' not in split_on_br_nodes[0]:
            raise ValueError(u'elem[0] needs to be h3: %s' % split_on_br_nodes[0])
        if 'D-DAY' not in split_on_br_nodes[1]:
            split_on_br_nodes.insert(1, 'Dummy D-DAY')
        if '' != split_on_br_nodes[3]:
            raise ValueError('uelem[3] should be empty: %s' % split_on_br_nodes[3])
        if u'장르' not in split_on_br_nodes[4]:
            raise ValueError(u'elem[4] should have 장르: %s' % split_on_br_nodes[4])
        if u'이벤트 타입' not in split_on_br_nodes[5]:
            raise ValueError(u'elem[5] should have 이벤트 타입: %s' % split_on_br_nodes[5])
        if '' != split_on_br_nodes[6]:
            raise ValueError(u'elem[6] should be empty; %s' % split_on_br_nodes[6])
        return (
            split_on_br_nodes[2],
            split_on_br_nodes[4],
            split_on_br_nodes[5],
        )

    def parse(self, response):
        if 'MainListGetMore.aspx' in response.url:
            return self.parseEventList(response)
        elif 'View.aspx' in response.url:
            return self.parseEvent(response)

    def parseEventList(self, response):
        event_ids = re.findall(r"openEventView\('(\d+)'\)", response.body)
        for i in event_ids:
            yield scrapy.Request('http://www.streetdancekorea.com/Event/View.aspx?seq=%s&bid=Event' % i)
        # As long as we found some events, keep fetching more pages of results
        if event_ids:
            qs = urlparse.parse_qs(urlparse.urlparse(response.url).query)
            qs = dict((k, v[0]) for (k, v) in qs.iteritems())
            qs['page'] = int(qs['page']) + 1
            url = 'http://www.streetdancekorea.com/Event/MainListGetMore.aspx'
            yield scrapy.Request('%s?%s' % (url, urllib.urlencode(qs)))

    def parseEvent(self, response):
        item = items.WebEvent()
        qs = urlparse.parse_qs(urlparse.urlparse(response.url).query)
        item['namespace'] = self.namespace
        item['namespaced_id'] = qs['seq'][0]
        item['name'] = strip_markdown.strip(items.extract_text(response.xpath('.//h3')))
        image_url = response.xpath('//img[@id="imgPoster"]/@src').extract()[0]
        if not image_url:
            return
        item['photo'] = urlparse.urljoin(response.url, image_url)

        nodes = response.css('.profile .desc').xpath('node()').extract()
        nodes = [x for x in [self._cleanup(x).strip() for x in nodes] if x]
        split_on_br_nodes = split_list_on_element(nodes, lambda x: x.startswith('<br') or x.startswith('<div'))

        date_string, style, event_type = self._validate(split_on_br_nodes)

        item['description'] = items.extract_text(response.css('.tab_info.desc'))

        item['start_time'], item['end_time'] = korean_dates.parse_times(date_string)

        # 'lg1=37.501771&lg2=126.770348&title=JB Dance Academy (부천시 원미구 중동 1151-4 이스트타워)'
        extract_location = r"lg1=(?P<latitude>[\d.]+)&lg2=(?P<longitude>[\d.]+)&title=(?P<venue>[^']+?)\((?P<address>[^']+?)\)\s*'"
        match = re.search(extract_location, response.body)
        if match:
            item['location_name'] = match.group('venue')
            item['location_address'] = match.group('address')
            item['latitude'] = match.group('latitude')
            item['longitude'] = match.group('longitude')
        else:
            # TODO: ...default to generic korea?
            logging.error("Found event with empty location: %s: %s", item['namespaced_id'], item['name'])
        yield item
