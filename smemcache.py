#!/usr/bin/env python

import pickle
import random
from google.appengine.api.memcache import *

def expiry_with_variance(expiry, expiry_variance):
  variance = expiry * expiry_variance
  return random.randrange(expiry - variance, expiry + variance)

def safe_set_memcache(memcache_set, expiry, top_level=True):
    set_size = len(pickle.dumps(memcache_set))
    if top_level:
        logging.info('set memcache size is %s' % set_size)
    # If it's roughly greater than a megabyte
    if set_size > 1024 * 1024 - 100:
        memcache_list = list(memcache_set.items())
        if len(memcache_list) == 1:
            logging.error("Saved item too large, cannot save, with key: %s", memcache_set.keys()[0])
            return
        halfway = len(memcache_list) / 2
        safe_set_memcache(dict(memcache_list[:halfway]), expiry, top_level=False)
        safe_set_memcache(dict(memcache_list[halfway:]), expiry, top_level=False)
    else:
        memcache.set_multi(memcache_set, expiry)

