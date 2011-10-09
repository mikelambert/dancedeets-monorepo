#!/usr/bin/python
import sys
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python']
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python/lib/yaml/lib']
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python/lib/webob']
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python/lib/fancy_urllib']
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python/lib/django']
sys.path += ['.']

import datetime
import sys
import time
import csv
import sqlite3
from google.appengine.datastore import entity_pb
from google.appengine.api import datastore

def flatten_output(db_name, out_name, process_func):
    ct = 0
    csvwriter = csv.writer(open(out_name, 'w'))
    conn = sqlite3.connect(db_name, isolation_level=None)
    cursor = conn.cursor()
    cursor.execute('select id, value from result')
    for unused_entity_id, entity in cursor:
        entity_proto = entity_pb.EntityProto(contents=entity)
        f = datastore.Entity._FromPb(entity_proto)
        try:
            result = process_func(f)
        except Exception, e:
            print "Error processing row %s: %s: %s" % (f.key().name(), e, f)
        csvwriter.writerow(result)

        ct += 1
        if ct % 20000 == 0:
            print "Ct is %s" % ct
            sys.stdout.flush()
    print "done"

def event_list(x):
    start_time = x.get('start_time') or datetime.datetime.min
    return [
        x.key().name(),
        str(x['owner_fb_uid']),
        ';'.join([y for y in x.get('tags', []) if not y.startswith('STYLE_')]),
        start_time.strftime('%Y%m%d')
    ]

flatten_output("local_data/DBEvent.db", "local_data/DBEvent.csv", event_list)
flatten_output("local_data/PotentialEvent.db", "local_data/PotentialEvent.csv", lambda x: [x.key().name()])
flatten_output("local_data/FacebookCachedObject.db", "local_data/FacebookCachedObject.csv", lambda x: [x.key().name(), x['json_data']])

# count characters
count_characters = True
if count_characters:
    from django.utils import simplejson
    conn = sqlite3.connect('local_data/FacebookCachedObject.db', isolation_level=None)
    cursor = conn.cursor()
    cursor.execute('select id, value from result')
    total = 0
    count = 0
    for unused_entity_id, entity in cursor:
        entity_proto = entity_pb.EntityProto(contents=entity)
        f = datastore.Entity._FromPb(entity_proto)
        print f.key().name()
        if f.key().name().endswith('OBJ_EVENT'):
            if 'json_data' in f:
                data = simplejson.loads(f['json_data'])
                if not data['deleted']:
                    total += len(data['info'].get('description', '')) or 0
                    count += 1
        
    print 'total characters', total
    print 'total events', ccount
    print 'characters per event', 1.0*total/count
