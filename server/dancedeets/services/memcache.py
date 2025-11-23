"""Memcache client abstraction layer.

This provides a consistent memcache API that works with:
- pylibmc (connecting to Memcached or Redis with memcache protocol)
- A simple in-memory fallback for development

For production, configure redis_memcache_endpoint in keys.
"""

import logging
import os

from dancedeets import keys

# Try to import pylibmc
try:
    import pylibmc
    HAS_PYLIBMC = True
except ImportError:
    logging.warning('pylibmc not available, using in-memory cache')
    HAS_PYLIBMC = False


class InMemoryCache:
    """Simple in-memory cache for development/testing."""

    def __init__(self):
        self._cache = {}

    def get(self, key):
        return self._cache.get(key)

    def get_multi(self, keys):
        return {k: self._cache[k] for k in keys if k in self._cache}

    def set(self, key, value, time=0):
        self._cache[key] = value
        return True

    def set_multi(self, mapping, time=0):
        self._cache.update(mapping)
        return []

    def delete(self, key):
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def delete_multi(self, keys):
        deleted = False
        for key in keys:
            if key in self._cache:
                del self._cache[key]
                deleted = True
        return deleted

    def flush_all(self):
        self._cache.clear()
        return True


def _init_memcache_client():
    """Initialize and return the appropriate memcache client."""
    # Check if we're in local development
    is_local = os.environ.get('GAE_ENV', '') != 'standard' and not os.environ.get('GOOGLE_CLOUD_PROJECT')

    # Try to get Redis/Memcache configuration
    endpoint = keys.get('redis_memcache_endpoint') if keys else None

    if endpoint and HAS_PYLIBMC:
        try:
            password = keys.get('redis_memcache_password')
            if password:
                client = pylibmc.Client(
                    [endpoint],
                    binary=True,
                    username='dancedeets',
                    password=password
                )
            else:
                client = pylibmc.Client([endpoint], binary=True)

            # Test the connection
            client.get('__test__')
            logging.info('Connected to memcache at %s', endpoint)
            return client
        except Exception as e:
            logging.warning('Failed to connect to memcache at %s: %s', endpoint, e)

    # Fall back to in-memory cache
    logging.info('Using in-memory cache')
    return InMemoryCache()


# Initialize the client
memcache_client = _init_memcache_client()


# Public API functions
def get(key):
    """Get a value from cache."""
    try:
        return memcache_client.get(key)
    except Exception as e:
        logging.error('Memcache get error: %s', e)
        return None


def get_multi(cache_keys):
    """Get multiple values from cache."""
    try:
        return memcache_client.get_multi(cache_keys)
    except Exception as e:
        logging.error('Memcache get_multi error: %s', e)
        return {}


def set(key, value, time=0):
    """Set a value in cache."""
    try:
        return memcache_client.set(key, value, time=time)
    except Exception as e:
        logging.error('Memcache set error: %s', e)
        return False


def set_multi(mapping, time=0):
    """Set multiple values in cache."""
    try:
        return memcache_client.set_multi(mapping, time=time)
    except Exception as e:
        logging.error('Memcache set_multi error: %s', e)
        return list(mapping.keys())


def delete(key):
    """Delete a value from cache."""
    try:
        return memcache_client.delete(key)
    except Exception as e:
        logging.error('Memcache delete error: %s', e)
        return False


def delete_multi(cache_keys):
    """Delete multiple values from cache."""
    try:
        return memcache_client.delete_multi(cache_keys)
    except Exception as e:
        logging.error('Memcache delete_multi error: %s', e)
        return False


def flush_all():
    """Flush all values from cache."""
    try:
        return memcache_client.flush_all()
    except Exception as e:
        logging.error('Memcache flush_all error: %s', e)
        return False
