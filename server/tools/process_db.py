#!/usr/bin/python
"""
DEPRECATED: This script requires the legacy App Engine SDK for entity_pb and datastore modules.
It was used for processing old datastore backups and may not work in App Engine Flexible Environment.

To use this script, you need the old App Engine SDK installed and available in your path.
"""
import sys
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python']
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python/lib/yaml/lib']
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python/lib/webob']
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python/lib/fancy_urllib']
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python/lib/django']
sys.path += ['.']

import csv
import datetime
import os
import sqlite3
import sys
from google.appengine.datastore import entity_pb
from google.appengine.api import datastore


def flatten_output(db_name, out_name, process_func):
    ct = 0
    print('Processing %s' % db_name)
    with open(out_name + ".new", 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        conn = sqlite3.connect(db_name, isolation_level=None)
        cursor = conn.cursor()
        cursor.execute('select id, value from result')
        for unused_entity_id, entity in cursor:
            entity_proto = entity_pb.EntityProto(contents=entity)
            f = datastore.Entity._FromPb(entity_proto)
            try:
                result = process_func(f)
                if result is not None:
                    csvwriter.writerow(result)
            except Exception as e:
                print("Error processing row %s: %r: %s" % (f.key().name(), e, f))

            ct += 1
            if ct % 20000 == 0:
                print("Ct is %s" % ct)
                sys.stdout.flush()
    os.rename(out_name, out_name + ".bak")
    os.rename(out_name + ".new", out_name)
    print("done")


def event_list(x):
    start_time = x.get('start_time') or datetime.datetime(1970, 1, 1)
    return [
        x.key().name(), x['owner_fb_uid'], ';'.join([y for y in x.get('tags', []) if not y.startswith('STYLE_')]),
        start_time.strftime('%Y%m%d')
    ]


def potential_event(x):
    return [x.key().name(), x.get('match_score', 0)]


def json_data(x):
    if 'json_data' in x:
        return [x.key().name(), x['json_data']]
    else:
        return None


flatten_output("local_data/DBEvent.db", "local_data/DBEvent.csv", event_list)
flatten_output("local_data/PotentialEvent.db", "local_data/PotentialEvent.csv", potential_event)
flatten_output("local_data/FacebookCachedObject.db", "local_data/FacebookCachedObject.csv", json_data)

# count characters
count_characters = False
if count_characters:
    import json
    conn = sqlite3.connect('local_data/FacebookCachedObject.db', isolation_level=None)
    cursor = conn.cursor()
    cursor.execute('select id, value from result')
    total = 0
    count = 0
    for unused_entity_id, entity in cursor:
        entity_proto = entity_pb.EntityProto(contents=entity)
        f = datastore.Entity._FromPb(entity_proto)
        if f.key().name().endswith('OBJ_EVENT'):
            if 'json_data' in f:
                data = json.loads(f['json_data'])
                if not data['empty']:
                    total += len(data['info'].get('description', '')) or 0
                    count += 1

    print('total characters', total)
    print('total events', count)
    print('characters per event', 1.0 * total / count)
