#!/usr/bin/python

import json
import os
import time
import urllib

if not os.path.exists('download'):
    os.makedirs('download')

def get_id(id):
    json_filename = 'download/%s.json' % id
    if not os.path.exists(json_filename):
        url = 'http://jamyo.jamyooo.com/Lite/Jam/jam_detail?id=%s' % id
        data = urllib.urlopen(url).read()
        open(json_filename, 'w').write(data)
        time.sleep(2)
    try:
        json_data = json.loads(open(json_filename).read())
    except ValueError:
        return None

    if json_data['status'] != 200:
        raise Exception(json_data)
    else:
        event = json_data['data']
        print event['id'], event['title'].encode('utf-8')
        return event
id = 1
while True:
    get_id(id)
    id += 1
