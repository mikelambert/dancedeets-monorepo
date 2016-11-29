#!/usr/bin/python
"""
# App Engine import data from Datastore Backup to localhost

You can use this script to import large(ish) App Engine Datastore backups to your localohst dev server.

## Getting backup files

Follow instructions from Greg Bayer's awesome article to fetch the App Engine backups:
http://gbayer.com/big-data/app-engine-datastore-how-to-efficiently-export-your-data/

Basically, download and configure gsutil and run:
```
gsutil -m cp -R gs://your_bucket_name/your_path /local_target
```

## Reading data to your local (dev_appserver) application

Copy-paste this gist to your Interactive Console, set correct paths and press `Execute`.
(default: http://localhost:8000/console)

"""
import sys
sys.path.insert(0, '/usr/local/google_appengine')

print sys.path
from google.appengine.api.files import records
from google.appengine.datastore import entity_pb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from google.appengine.ext import ndb
from os.path import isfile
from os.path import join
from os import listdir

from events.eventdata import DBEvent

def run():
    # Set your downloaded folder's path here (must be readable by dev_appserver)
    mypath = '/Users/lambert/Dropbox/dancedeets-data/datastore_backup_datastore_backup_2016_11_19_DBEvent/15700286559371541387849311E815D'
    # Se the class of the objects here
    cls = DBEvent
    # Set your app's name here
    appname = "dev~None"

    # Do the harlem shake
    onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]

    for file in onlyfiles:
        i = 0
        try:
            raw = open(mypath + "/" + file, 'r')
            reader = records.RecordsReader(raw)
            to_put = list()
            for record in reader:
                entity_proto = entity_pb.EntityProto(contents=record)
                entity_proto.key_.app_ = appname
                obj = cls._from_pb(entity_proto)

                to_put.append(obj)
                i += 1
                if i % 100 == 0:
                    print "Saved %d %ss" % (i, '')#entity.kind())
                    ndb.put_multi(to_put) # use_memcache=False)
                    to_put = list()

            ndb.put_multi(to_put) # use_memcache=False)
            to_put = list()
            print "Saved %d" % i

        except ProtocolBufferDecodeError:
            """ All good """

run()
