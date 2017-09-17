import logging
import pylibmc

try:
    from google.appengine.api import memcache as gae_memcache
except ImportError:
    logging.error('Failed to import memcache')
    gae_memcache = None

from dancedeets import keys


def init_memcache():
    client = pylibmc.Client([keys.get('redis_memcache_endpoint')],
                            binary=True,
                            username='dancedeets',
                            password=keys.get('redis_memcache_password'))

    # Non-existent functions necessary to adhere to the memcache API expected by gae_memcache's setup_client()
    client.set_servers = None
    client.forget_dead_hosts = None
    client.debuglog = None
    client.replace_multi = None
    client.offset_multi = None
    if gae_memcache:
        # Try to use this redis memcache for all GAE stuff seamlessly
        gae_memcache.setup_client(client)
    return client


from dancedeets.util import runtime
if runtime.is_local_appengine():
    memcache_client = gae_memcache._CLIENT
else:
    # TODO: enable this Redis memcache (and pay for it) when we need to switch off the built-in GAE memcache
    # memcache_client = init_memcache()
    pass

# Expose a simplified memcache_client API here...will we need it at all?


def get(key):
    return memcache_client.get(key)


def get_multi(keys):
    return memcache_client.get_multi(keys)


def set(key, value, time=0):
    return memcache_client.set(key, value, time=time)


def set_multi(mapping, time=0):
    return memcache_client.set(mapping, time=time)


def flush_all():
    return memcache_client.flush_all()


def delete(key):
    return memcache_client.delete(key)


def delete_multi(keys):
    return memcache_client.delete_multi(keys)
