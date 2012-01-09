"""module for tracking time spent so we know where our quota goes and how to optimize"""

import logging
import time

from google.appengine.api import memcache

MEMCACHE_TIMING_PREFIX = 'timing.'

MEMCACHE_NAMES_KEY = 'timing_names'

def name_of(func):
    """probably broken function to get the full name of a function for use in stats recording"""
    if hasattr(func, 'im_class'):
        return '%s.%s' % (name_of(func.im_class), func.__name__)
    elif hasattr(func, 'im_self'):
        return '%s.%s' % (name_of(func.im_self.__class__), func.__name__)
    else:
        return '%s.%s' % (func.__module__, func.__name__)

def timed(func):
    name = name_of(func)
    def _func(*args, **kwargs):
        a = time.time()
        try:
            ret = func(*args, **kwargs)
        finally:
            accum = time.time() - a
            logging.info("Accumulating %s seconds for %s", accum, name)
            accumulate_time(name, accum)
        return ret
    return _func

def _key_for_name(name):
    return '%s%s' % (MEMCACHE_TIMING_PREFIX, name)

def accumulate_time(name, time):
    memcache_key = _key_for_name(name)
    incremented = memcache.incr(memcache_key, delta=int(time*1000), initial_value=0) #in milliseconds
    logging.info('incremented is %s', incremented)

    names = memcache.get(MEMCACHE_NAMES_KEY)
    if not names:
        names = set()
    if name not in names:
        names.add(name)
        memcache.set(MEMCACHE_NAMES_KEY, names)

def clear_all():
    names = memcache.get(MEMCACHE_NAMES_KEY) or set()
    memcache.delete(MEMCACHE_NAMES_KEY)
    for name in names:
        memcache_key = _key_for_name(name)
        memcache.delete(name)
    
def keep_alive():
    names = memcache.get(MEMCACHE_NAMES_KEY) or set()
    memcache.get_multi([_key_for_name(name) for name in names])

def summary():
    names = memcache.get(MEMCACHE_NAMES_KEY) or set()
    name_timings = memcache.get_multi(names, _key_for_name(''))
    return name_timings

