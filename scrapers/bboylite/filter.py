#!/usr/bin/python

import json
import os


def is_good(data):
    phone = (data['data']['phone'] or '').replace('-', '')
    if phone and len(phone) != 11:
        return False
    if data['data']['title'] == '':
        return False
    return True


dir = 'download-jam'
for filename in os.listdir(dir):
    data_text = open('%s/%s' % (dir, filename)).read()
    try:
        data = json.loads(data_text)
    except ValueError:
        continue
    if not is_good(data):
        continue
    title = data['data']['title'].strip()
    print data['data']['startDate'], data['data']['id'], title.encode('utf-8')
    #if data['data']['isPass'] != 1:

# TODO:
# - need to support multiple image downloading for a single event
# - Don't use scrapy, since its not html
# - Find future ids, and refetch them.
# - Find highest known id, and fetch new ones from there
# - at some point, trim off watermarks:
# http://7xqfjm.com2.z0.glb.qiniucdn.com/146164906300045.jpg?watermark/1/image/aHR0cDovL2p3amFtLmNvbS9QdWJsaWMvSW5kZXgvaW1hZ2VzL2xvZ28ucG5n/dissolve/50/gravity/SouthEast/dx/10/dy/10
