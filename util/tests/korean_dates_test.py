# -*-*- encoding: utf-8 -*-*-

import datetime
import unittest

from util import korean_dates

examples = {
    u'2016년 3월 12일(토)': (datetime.date(2016, 3, 12), None),
    u'2016년 3월 20일(일), 오후 2시': (datetime.datetime(2016, 3, 20, 12 + 2), None),
    u'2016년 3월 5일(토), 오후 7시 ~ 10시': (datetime.datetime(2016, 3, 5, 12 + 7), datetime.datetime(2016, 3, 5, 12 + 10)),
    u'2016년 3월 6일(일), 오후 5시 ~ 오후 10시': (datetime.datetime(2016, 3, 6, 12 + 5), datetime.datetime(2016, 3, 6, 12 + 10)),
    u'2016년 3월 4일(금), 오후 7시부터': (datetime.datetime(2016, 3, 4, 12 + 7), None), # pm 7 from
    u'2016년 3월 12일(토), 예선 오후 1시부터': (datetime.datetime(2016, 3, 12, 12 + 1), None), # qualifier pm 1 from
    u'2016년 3월 11일(금) / 3월 12일(토)': (datetime.date(2016, 3, 11), datetime.date(2016, 3, 12)),
    u'2016년 3월 26일(토) ~ 27일(일)': (datetime.date(2016, 3, 26), datetime.date(2016, 3, 27)),
    u'2016년 3월 5일(토), 밤 11시부터 새벽': (datetime.datetime(2016, 3, 5, 12 + 11), datetime.datetime(2016, 3, 5, korean_dates.DAWN)), # "at 11pm (until)dawn"
    u'2016년 3월 6일(일), 오후 3시 30분': (datetime.datetime(2016, 3, 6, 12 + 3, 30), None), # pm 3 : 30
    u'2016년 3월 1일(화), 오후 5시~': (datetime.datetime(2016, 3, 1, 12 + 5), None), # extraneous ~
    u'2016년 3월 5일(토), 오후 4시 ~ 6시': (datetime.datetime(2016, 3, 5, 12 + 4), datetime.datetime(2016, 3, 5, 12 + 6)),
    u'2016년 3월 19일(토), 오후 3시~6시': (datetime.datetime(2016, 3, 19, 12 + 3), datetime.datetime(2016, 3, 19, 12 + 6)),
    u'2016년 3월 13일(토), 예선 오후 2시, 본선 오후 5시': (datetime.datetime(2016, 3, 13, 12 + 2), None),  # qualifying pm 2, finals pm 5
    u'2016년 3월 6일 일요일, 오후 1시부터': (datetime.datetime(2016, 3, 6, 12 + 1), None), # sunday, pm 1 from
    u'2016년 3월 12일, 팝핀 예선 2시, 락킹 예선 4시': (datetime.datetime(2016, 3, 12, 12 + 2), None), # popping qualifying 2, locking qualifying 4
    u'2016년 3월 13일, 오후 6시 30분부터': (datetime.datetime(2016, 3, 13, 12 + 6, 30), None), # pm 6 : 30 from
    u'2016년 4월 3일(일), 오후 1시, 오후 6시 30분': (datetime.datetime(2016, 4, 3, 12 + 1), None), # pm 1, pm 6 : 30
    u'2016년 4월 30일(토), 오후 2시 ~': (datetime.datetime(2016, 4, 30, 12 + 2), None),
    u'2016년 4월 30일(토), 시간 추후 공지': (datetime.date(2016, 4, 30), None), # hours later notice (aka TBA)
    u'2016년 4월 16일(토), 오후 3시 ~ 8시': (datetime.datetime(2016, 4, 16, 12 + 3), datetime.datetime(2016, 4, 16, 12 + 8)),
    u'2016년 4월 10일(일), 시간 추후공지': (datetime.date(2016, 4, 10), None), # hours laternotice
    u'2016년 4월 3일(일), 예선 오후 1시': (datetime.datetime(2016, 4, 3, 12 + 1), None), # qualifying pm 1
    u'2016년 2월 29일(월), 오후 8시부터': (datetime.datetime(2016, 2, 29, 12 + 8), None),
    u'2016년 2월 28일(일), 오후 2시 ~ 3시 30분': (datetime.datetime(2016, 2, 28, 12 + 2), datetime.datetime(2016, 2, 28, 12 + 3, 30)),
    # I've technically filled out incorrect data on this result. Because it's ambiguous as to the meaning of the / character (see above)
    u'2016년 2월 27일(토), 예선 오후 1시 / 본선 오후 4시 30분': (datetime.datetime(2016, 2, 27, 12 + 1), datetime.datetime(2016, 2, 27, 12 + 4, 30)), # prelim pm 1 / main pm 4 : 30
    u'2016년 2월 27일(토),': (datetime.date(2016, 2, 27), None),
    u'2016년 2월 28일(일), 오후 2시, 오후 6시': (datetime.datetime(2016, 2, 28, 12 + 2), None),
    # This one's result feels dangerous...but 11pm was meant, and every event seems to start in pm anyway
    u'2016년 2월 27일(토), 밤 11시': (datetime.datetime(2016, 2, 27, 12 + 11), None), # at 11
    u'2016년 2월 20일(토), 예선 시작 오후 1시': (datetime.datetime(2016, 2, 20, 12 + 1), None), # qualifying begins pm 1
    u'2016년 2월 20일(토), 오후 8시부터 입장': (datetime.datetime(2016, 2, 20, 12 + 8), None), # pm 8 from entry
    u'2016년 2월 26일(금). 밤 11시 30분부터 ~': (datetime.datetime(2016, 2, 26, 12 + 11, 30), None),
    u'2016년 2월 27일 토요일, 4시 입장 entry': (datetime.datetime(2016, 2, 27, 12 + 4), None),
    u'2016년 2월 13일 토요일, 3시부터 6시까지': (datetime.datetime(2016, 2, 13, 12 + 3), datetime.datetime(2016, 2, 13, 12 + 6)), # 3 from 6 until
    u'2016년 2월 27일 토요일, 오후 1시부터 입장': (datetime.datetime(2016, 2, 27, 12 + 1), None), # pm 1 from entry
    u'2016년 2월 20일 토요일, 힙합 예선 2시, 왁킹 예선 3시, 본선 5시 30분부터': (datetime.datetime(2016, 2, 20, 12 + 2), None), # hiphop pm 2, waacking pm 3, main 5 : 30 from
    u'2016년 2월 14일 일요일': (datetime.date(2016, 2, 14), None),
    u'2016년 4월 3일(일), 오전 11시': (datetime.datetime(2016, 4, 3, 11), None), # am 11
    u'2016년 3월 19일(토), 오후 12시': (datetime.datetime(2016, 3, 19, 12), None), # pm 12 (make sure it's noon!)
    u'2016녀 5월 5일(목), 오후 2시부터': (datetime.datetime(2016, 5, 5, 12 + 2), None),
    u'2016년 4월 15(금), 오후 8시 ~ 10시': (datetime.datetime(2016, 4, 15, 12 + 8), datetime.datetime(2016, 4, 15, 12 + 10)),
}


class TestParseFbTimestamp(unittest.TestCase):
    def runTest(self):
        for s, expected_result in examples.iteritems():
            result = korean_dates.parse_times(s)
            self.assertEqual(result, expected_result)
