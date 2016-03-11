# -*-*- encoding: utf-8 -*-*-

import re

prefectures = [
    u'愛知県',
    u'秋田県',
    u'青森県',
    u'千葉県',
    u'愛媛県',
    u'福井県',
    u'福岡県',
    u'福島県',
    u'岐阜県',
    u'群馬県',
    u'広島県',
    u'北海道',
    u'兵庫県',
    u'茨城県',
    u'石川県',
    u'岩手県',
    u'香川県',
    u'鹿児島県',
    u'神奈川県',
    u'高知県',
    u'熊本県',
    u'京都府',
    u'三重県',
    u'宮城県',
    u'宮崎県',
    u'長野県',
    u'長崎県',
    u'奈良県',
    u'新潟県',
    u'大分県',
    u'岡山県',
    u'沖縄県',
    u'大阪府',
    u'佐賀県',
    u'埼玉県',
    u'滋賀県',
    u'島根県',
    u'静岡県',
    u'栃木県',
    u'徳島県',
    u'東京都',
    u'鳥取県',
    u'富山県',
    u'和歌山県',
    u'山形県',
    u'山口県',
    u'山梨県',
]

prefectures_re_text = '(?:%s)' % '|'.join(prefectures)

address_re_text = ur'%s\S{2,10}[市郡区]\S+' % prefectures_re_text

address_re = re.compile(address_re_text)

def find_addresses(s):
    return address_re.findall(s)
