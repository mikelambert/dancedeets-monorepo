from atomicwrites import atomic_write
import sqlite3
import getpass
import logging
import os
import threading
import time

from google.cloud import storage

from dancedeets.util import runtime
from dancedeets.util import timelog

DEV_PATH = '/Users/%s/Dropbox/dancedeets-development/server/generated/' % getpass.getuser()
SERVER_PATH = os.path.dirname(os.path.realpath(__file__))

FILE_COPY_LOCK = threading.Lock()


def _download_sqlite(db_path):
    logging.info('Grabbing file-copy lock')
    if FILE_COPY_LOCK.acquire():
        # Check it again, now that we've finally gotten the lock
        logging.info('Grabbed lock, checking if file exists: %s', os.path.exists(db_path))
        if not os.path.exists(db_path):
            # TODO: ensure we copy to a staging ground, and move it into place (so no one tries to open a malformed file)
            client = storage.Client('dancedeets-hrd')
            bucket = client.get_bucket('dancedeets-dependencies')
            logging.info('Downloading file')
            blob = bucket.get_blob(os.path.basename(db_path))
            # Luckily this only takes around 5-10 seconds (for street dance) when run on GCE instances
            contents = blob.download_as_string()
            with atomic_write(db_path, overwrite=True) as f:
                f.write(contents)
                # db_path doesn't exist yet.
            # Now it does.
        FILE_COPY_LOCK.release()


def get_connection(database_name, fallback_database_name=None):
    full_db_name = '%s.db' % database_name
    if os.environ.get('TRAVIS') or runtime.is_local_appengine():
        db_path = os.path.join(DEV_PATH, full_db_name)
        if not os.path.exists(db_path):
            db_path = fallback_database_name
    else:
        db_path = os.path.join(SERVER_PATH, full_db_name)
        if not os.path.exists(db_path):
            start = time.time()
            _download_sqlite(db_path)
            timelog.log_time_since('Downloading PRCityCategory sqlite db', start)
    conn = sqlite3.connect(db_path)
    # Cannot be shared between threads, be careful if making this global!
    return conn
