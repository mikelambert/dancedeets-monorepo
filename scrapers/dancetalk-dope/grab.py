#!/usr/bin/python

import json
import os
import time
import urllib

if not os.path.exists('download'):
    os.makedirs('download')

# Mix of streetdance.wang (autoincrement ids) and dope.ren (hashed ids?)


def get_data(url):
    print url
    data = urllib.urlopen(url).read()
    return json.loads(data)


def get_list():
    first_data = get_data('https://www.dope.ren/dope/activity/twoCondition.do?startPage=1')
    activities = []
    for i in range(first_data['activityTotalPage']):
        new_data = get_data('https://www.dope.ren/dope/activity/twoCondition.do?startPage=%s' % (i + 1))
        open('download/twoCondition%s.json' % (i + 1), 'w').write(json.dumps(new_data))
        activities.extend(new_data['activity'])
    # No longer works:
    # data = urllib.urlopen('https://www.dope.ren/dope/activity/condition.do').read()

    data = {'activity': activities, 'activityTotalPage': first_data['activityTotalPage']}
    open('download/twoCondition.json', 'w').write(json.dumps(data))
    return data


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
