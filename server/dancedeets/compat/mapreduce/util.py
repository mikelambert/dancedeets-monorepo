"""Stub for mapreduce.util"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.util import *
else:
    import inspect

    # Constants used by mapreduce
    _MR_SHARD_ID_TASK_HEADER = 'X-AppEngine-MapReduce-ShardId'
    _MR_ID_TASK_HEADER = 'X-AppEngine-MapReduce-Id'

    def is_generator(func):
        """Check if a function is a generator"""
        return inspect.isgeneratorfunction(func)

    def _get_task_host():
        return None

    def strip_prefix_from_items(prefix, items):
        """Strip prefix from a list of items"""
        return [item[len(prefix):] if item.startswith(prefix) else item for item in items]

    def create_datastore_write_config(mapreduce_spec):
        """Stub create_datastore_write_config"""
        return None
