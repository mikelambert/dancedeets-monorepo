#!/usr/bin/python

import json
import os
import urllib

JAM = {'dir': 'download-jam', 'url': 'http://jamyo.jamyooo.com/Lite/Jam/jam_detail?id=%s'}
COURSE = {'dir': 'download-course', 'url': 'https://jamyo.jamyooo.com/Lite/Course/course_details?course_id=%s'}


def get_id(id, type):
    if not os.path.exists(type['dir']):
        os.makedirs(type['dir'])
    json_filename = '%s/%s.json' % (type['dir'], id)
    if not os.path.exists(json_filename):
        url = type['url'] % id
        data = urllib.urlopen(url).read()
        open(json_filename, 'w').write(data)
        #time.sleep(2)
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


trailing_count = 20


def grab_all(start_id, type):
    missing = 0
    id = start_id
    while True:
        event = get_id(id, type)
        id += 1

        if event:
            missing = 0
        else:
            missing += 1
        if missing >= trailing_count:
            break
    last_id = id - missing

    # And this will then clean them all up
    delete_past(last_id, type)

    return last_id


def delete_past(id, type):
    for i in range(0, trailing_count + 1):
        json_filename = '%s/%s.json' % (type['dir'], id + i)
        if os.path.exists(json_filename):
            os.remove(json_filename)


# This will accidentally create a few 'empty' files at the very end..
#last_id = grab_all(3167, JAM)
last_id = grab_all(92, COURSE)
