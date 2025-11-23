#!/usr/bin/python
"""
DEPRECATED: This script requires the legacy App Engine SDK for entity_pb and datastore modules.
It was used for dumping FacebookCachedObject data and may not work in App Engine Flexible Environment.

To use this script, you need the old App Engine SDK installed and available in your path.
"""
import sqlite3

import sys
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python']
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python/lib/yaml/lib']
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python/lib/webob']
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python/lib/fancy_urllib']
sys.path += ['/Users/lambert/Projects/googleappengine-read-only/python/lib/django']
sys.path += ['.']

from google.appengine.datastore import entity_pb
from google.appengine.api import datastore

conn = sqlite3.connect('local_data/FacebookCachedObject.db', isolation_level=None)
cursor = conn.cursor()
cursor.execute('select id, value from result')
for entity_id, entity in cursor:
    entity_proto = entity_pb.EntityProto(contents=entity)
    e = datastore.Entity._FromPb(entity_proto)
    if str(entity_id).endswith('OBJ_EVENT'):
        real_id = str(entity_id).split(':')[-1]
        if 'json_data' in e:
            with open('test_data/FacebookCachedObject/%s' % real_id, 'w') as f:
                f.write(e['json_data'])
