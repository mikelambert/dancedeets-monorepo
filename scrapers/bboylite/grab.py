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


trailing_count = 5


def grab_all():
    id = 2860
    missing = 0
    while True:
        event = get_id(id)
        id += 1

        if event:
            missing = 0
        else:
            missing += 1
        if missing > trailing_count:
            break
    return id - missing


def delete_past(id):
    for i in range(0, trailing_count):
        json_filename = 'download/%s.json' % (id + i)
        os.remove(json_filename)


# This will accidentally create a few 'empty' files at the very end..
last_id = grab_all()
# And this will then clean them all up
delete_past(last_id)
