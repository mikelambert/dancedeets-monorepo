
_cache = {}

def set(key, value, time=0):
  set_multi({key:value},time)

def set_multi(mapping, time=0):
    _cache.update(mapping)

def get(key):
    return _cache.get(key)

def get_multi(keys):
    return dict([(k,_cache.get(k)) for k in keys if k in _cache])

def flush_all():
    global _cache
    _cache = {}
