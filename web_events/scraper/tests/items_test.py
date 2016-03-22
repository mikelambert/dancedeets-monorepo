# -*-*- encoding: utf-8 -*-*-

import logging
import unittest

from web_events.scraper import items


class TestLineAfter(unittest.TestCase):
    tests = {
        u"""【会場】 HARLEM　PLUS\n""":
        u'HARLEM　PLUS',
        u"""場所

本郷台あーすぷらざ
        """:
        u'本郷台あーすぷらざ',
        u"""場所

＠東大和市民会館ハミングホール 大ホール
（西武拝島線東大和駅より徒歩10分）
東京都東大和市向原6-1
※新宿から約50分""":
        u'東大和市民会館ハミングホール 大ホール',
        #u"""※会場が変更になりました""":
        #'',
        u"""場所

両国国技館""":
        u'両国国技館',
        u"""場所

Mt.RAINIER HALL SHIBUYA PLEASURE PLEASURE""":
        u'Mt.RAINIER HALL SHIBUYA PLEASURE PLEASURE',
        u"""場所

DIFFER有明""":
        u'DIFFER有明',
        u"""場所

CLUB CITTA'""":
        u"CLUB CITTA'",
        u"""【場所】グランフロント大阪 うめきた広場テントステージ""":
        u'グランフロント大阪 うめきた広場テントステージ',
        u"""＊HIPHOP&HOUSEエントリー者は11:30までに会場集合
＊FREESTYLE&BREAKエントリー者は12:00までに 会場集合

場所
金沢市民芸術村パフォーミングスクエア／石川
〒920-0046　石川県金沢市大和町1-1
        """: u'金沢市民芸術村パフォーミングスクエア／石川',
        u"""場所

HKラウンジ(JR橋本駅より徒歩約10分)""":
        u'HKラウンジ',
    }

    def runTest(self):
        for test, expected_result in self.tests.iteritems():
            logging.info("Testing: %s", test)
            result = items.get_line_after(test, ur'場所|会場|LOCATION|アクセス')
            self.assertEqual(result, expected_result, 'Found %s when parsing %s' % (result, test))
