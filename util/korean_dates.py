# -*-*- encoding: utf-8 -*-*-

import datetime
import re

DAWN = 6 # sun rises at 6am-ish


_DATETIME_SPAN_SEPARATOR = ur'(?:~|/|부터)'  # '부터' = 'from'


_D_DATE = ur'(?P<day>\d+)일'
_MD_DATE = ur'(?:(?P<month>\d+)월\s*)?' + _D_DATE
_YMD_DATE = ur'(?:(?P<year>\d+)년\s*)?' + _MD_DATE

# WEEKDAY = r'(?:\(.\)| ..일)?'

_AM_PM_TIME = ur'(?:(?P<ampm>오후|오전) )?(?P<hour>\d+)시 ?(?:(?P<minute>\d+)분|(?P<half>반))?'
_TIME = ur'(?:(?P<dawn>새벽)|%s)' % _AM_PM_TIME


def _extract_date(m, date_default=None):
    return datetime.date(int(m.group('year') or date_default.year), int(m.group('month') or date_default.month), int(m.group('day') or date_default.day))


def _extract_time(m, time_default=None):
    if m.group('dawn'):
        return datetime.time(DAWN)
    if m.group('half'):
        minute = 30
    else:
        minute = int(m.group('minute') or 0)
    if unicode(m.group('ampm')) == u'오후':
        ampm_offset = 12
    elif m.group('ampm') == u'오전':
        ampm_offset = 0
    else:
        ampm_offset = 12
    return datetime.time(int(m.group('hour')) + ampm_offset, minute)


def parse_times(s):
    elems = re.split(_DATETIME_SPAN_SEPARATOR, s, 2)
    if len(elems) == 1:
        start_str, end_str = elems[0], None
    else:
        start_str, end_str = elems[0], elems[1]

    start_date_match = re.search(_YMD_DATE, start_str)
    start_time_match = re.search(_TIME, start_str)

    start_datetime = _extract_date(start_date_match)
    if start_time_match:
        start_datetime = datetime.datetime.combine(start_datetime, _extract_time(start_time_match))

    end_datetime = None
    if end_str:
        end_date_match = re.search(_YMD_DATE, end_str)
        end_time_match = re.search(_TIME, end_str)
        if end_date_match or end_time_match:
            if end_date_match:
                end_datetime = _extract_date(end_date_match, date_default=start_datetime)
            else:
                if isinstance(start_datetime, datetime.datetime):
                    end_datetime = start_datetime.date()
                else:
                    end_datetime = start_datetime

            if end_time_match:
                end_datetime = datetime.datetime.combine(end_datetime, _extract_time(end_time_match))

    return (start_datetime, end_datetime)
