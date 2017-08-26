#!/usr/bin/python

import json
import os
import time
import urllib

if not os.path.exists('download'):
    os.makedirs('download')

# Mix of streetdance.wang (autoincrement ids) and dope.ren (hashed ids?)


def get_list():
    json_filename = 'condition.json'
    data = urllib.urlopen('https://www.dope.ren/dope/activity/condition.do').read()
    open(json_filename, 'w').write(data)
    return json.loads(data)


def get_id(id):
    json_filename = 'download/%s.json' % id
    if not os.path.exists(json_filename):
        url = 'https://www.dope.ren/dope/activity/twoGetById.do?id=%s' % id
        data = urllib.urlopen(url).read()
        open(json_filename, 'w').write(data)
        time.sleep(2)
    try:
        json_data = json.loads(open(json_filename).read())
    except ValueError:
        return None
    return json_data['activity']['data']


print 'list'
data = get_list()
for x in data['activity']:
    print 'fetching', x['id'], x.get('name')
    get_id(x['id'])
