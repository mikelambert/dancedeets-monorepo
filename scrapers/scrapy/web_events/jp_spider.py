# -*-*- encoding: utf-8 -*-*-

import datetime
import logging
import re

from . import items

open_time_re = ur'OPEN\W+\b(\d\d?):(\d\d)\b|(\d\d?):(\d\d)\W*OPEN|(\d\d?):(\d\d)\s*～'
close_time_re = ur'CLOSE(?:\s*予定)?\W+\b(\d+):(\d\d)\b'
open_close_time_re = ur'(\d\d?):(\d\d)\s*[～\-]\s*(\d\d?):(\d\d)'


def _intall(lst):
    return [None if x is None else int(x) for x in lst]


def _find_at_venue(text):
    # This is because some far-future events have no event information other than:
    # "2016年12月11日（日）@CONPASS", and we'd like to extract these locations as a last resort.
    at_lines = re.findall(ur'[＠@]([^\n]+)$', text, flags=re.MULTILINE)
    for x in at_lines:
        # So grab whatever comes after the @ sign as our venue name,
        # but ignore lowercase stuff (twitter handles, email address domains)
        if not re.match(r'^[a-z._\-]+$', x):
            x = re.sub(r'\(.*\)', '', x)
            return x
    return None


def _good_venue(venue):
    return venue and (u'年' not in venue)


def get_venue_from_description(description):
    venue = items.get_line_after(description, ur'場所|会場|LOCATION|アクセス')
    if not _good_venue(venue):
        venue = _find_at_venue(description)
    return venue


_VENUE_REMAP = {
    u'JANUS': u'JANUS, Osaka',
    u'江坂CAT HALL': u'キャットミュージックカレッジ',
    u'CATHALL': u'キャットミュージックカレッジ',
    u'CAT HALL': u'キャットミュージックカレッジ',
    u'HARLEM': u'Harlem, Shibuya',
    u'渋谷HAREM': u'Harlem, Shibuya',
    u'HARLEM　PLUS': u'Harlem, Shibuya',
    u'Neo Brotherz': u'Space Zero, 宮城',
    u'ARCHE': u'大宮アルシェ',
    u'天神 club selecta': u'club selecta 福岡県',
    u'ＨＡＴＣＨ！！～ＳＨＩＢＵＹＡ　ＲＥＮＴＡＬ　ＳＴＵＤＩＯ～': 'Studio Hatch, Shibuya',
    u'うめきた広場 テントステージ': u'グランフロント大阪 うめきた広場テントステージ',
    u'Studio 1000 / Studio NY': u'大阪市北区兎我野町5-6',
    u'darwin': u'Sendai Darwin',
}


def setup_location(venue, addresses, item):
    if venue:
        if venue in _VENUE_REMAP:
            logging.info('Rewriting venue %s as %s', venue, _VENUE_REMAP[venue])
            venue = _VENUE_REMAP[venue]
        item['location_name'] = venue
        item['geolocate_location_name'] = '%s, japan' % venue
    if addresses:
        item['location_address'] = addresses[0]


def parse_date_times(start_date, date_str):
    date_str = date_str.upper()
    open_time = None
    close_time = None

    open_match = re.search(open_time_re, date_str)
    if open_match:
        open_time = _intall(open_match.groups())
        # Keep trimming off groups of 2 until we find valid values
        while open_time[0] is None:
            open_time = open_time[2:]
        close_match = re.search(close_time_re, date_str)
        if close_match:
            close_time = _intall(close_match.groups())

    open_close_match = re.search(open_close_time_re, date_str)
    if open_close_match:
        open_close_time = _intall(open_close_match.groups())
        open_time = open_close_time[0:2]
        close_time = open_close_time[2:4]

    start_datetime = start_date
    if open_time:
        # We use timedelta instead of time, so that we can handle hours=24 or hours=25 as is sometimes used in Japan
        start_timedelta = datetime.timedelta(hours=open_time[0], minutes=open_time[1])
        start_datetime = datetime.datetime.combine(start_date, datetime.time()) + start_timedelta

    end_datetime = None
    if close_time:
        end_timedelta = datetime.timedelta(hours=close_time[0], minutes=close_time[1])
        end_datetime = datetime.datetime.combine(start_date, datetime.time()) + end_timedelta
        if end_datetime < start_datetime:
            end_datetime += datetime.timedelta(days=1)

    return start_datetime, end_datetime
