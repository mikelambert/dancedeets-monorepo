"""Stub for mapreduce.context"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.context import *
else:
    # Constants used by mapreduce handlers
    COUNTER_MAPPER_CALLS = 'mapper-calls'
    COUNTER_MAPPER_WALLTIME_MS = 'mapper-walltime-ms'

    class _StubCounters:
        """Stub counters that do nothing"""
        @staticmethod
        def increment(key, delta=1):
            pass

    class _StubContext:
        """Stub context that returns None for counter operations"""
        counters = _StubCounters()
        mapreduce_spec = None

    _context = None

    def get():
        """Return None when mapreduce is disabled"""
        return _context

    class Context:
        """Stub Context class"""
        _local = None

        @classmethod
        def _set(cls, context):
            cls._local = context
