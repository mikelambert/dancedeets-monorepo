# -*-*- encoding: utf-8 -*-*-

import unittest

from loc import japanese_addresses

examples = [
    u'〒150-0043 渋谷区道玄坂2-14-8',
    u'〒130-0015 東京都墨田区横網1−3−28',
    u'〒130-0015\n東京都墨田区横網1-3-28 / JR総武線各駅停車・都営地下鉄大江戸線：両国駅',
    u'目黒区勤労福祉会\n〒153-0063\n東京都目黒区目黒2-4-36',
    u'〒530-0026 大阪府大阪市北区神山町14−3',
    u'東京都杉並区荻窪5-11-15',
    u'大阪市北区神山町14－3　アド神山302',
]

negative_examples = [
    # Don't match on "wards"
    u'WORLD OF DANCEのSNSは、世界30万人を超えイベントに参加することで、全世界にプロモーションすることができます。作品性が認められれば、自分のPR以外に世界からのオファーや、企業がスポンサーに付くなど可能性が広がります。そして、ダンサーの栄誉でもある"World of Dance Awards"へのチャンスにもなります。',
]


class TestParseFbTimestamp(unittest.TestCase):
    def runTest(self):
        for s in examples:
            self.assert_(japanese_addresses.find_addresses(s), s.encode('utf-8'))
        for s in negative_examples:
            self.assertFalse(japanese_addresses.find_addresses(s), s.encode('utf-8'))
