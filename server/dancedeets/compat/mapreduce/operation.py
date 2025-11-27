"""Stub for mapreduce.operation"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.operation import *
else:
    class db:
        @staticmethod
        def Put(entity):
            """Stub put operation - actually performs the put"""
            if hasattr(entity, 'put'):
                entity.put()

        @staticmethod
        def Delete(entity):
            """Stub delete operation"""
            if hasattr(entity, 'key'):
                entity.key.delete()

    class counters:
        @staticmethod
        def Increment(key, delta=1):
            """Stub counter increment"""
            pass
