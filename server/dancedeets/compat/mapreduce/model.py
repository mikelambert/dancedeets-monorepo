"""Stub for mapreduce.model"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.model import *
else:
    class ShardState:
        """Stub ShardState"""
        slice_id = 0
        active = False
        result_status = None
        input_finished = False

        def copy_from(self, other_state):
            pass

        def set_for_failure(self):
            self.active = False
            self.result_status = 'failed'

        def put(self, config=None):
            pass

        @staticmethod
        def get_key_by_shard_id(shard_id):
            return None

    class MapreduceState:
        """Stub MapreduceState"""
        counters_map = None

        @staticmethod
        def get_key_by_job_id(job_id):
            return None

        @staticmethod
        def gql(query_string, **kwargs):
            return _StubQuery()

    class _StubQuery:
        """Stub GQL query"""
        def fetch(self, limit):
            return []
