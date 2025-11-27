"""Stub for mapreduce.handlers"""

import logging
import time
from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.handlers import *
else:
    class MapperWorkerCallbackHandler:
        """Stub handler - MapReduce is disabled in Flex environment"""

        def __init__(self, *args, **kwargs):
            self._start_time = time.time()
            self.slice_context = _StubSliceContext()

        def _time(self):
            return time.time()

        def _processing_limit(self, mapreduce_spec):
            return 100

        def _process_inputs(self, input_reader, shard_state, tstate, ctx):
            logging.warning("MapReduce is disabled, _process_inputs is a no-op")
            return True

        def _process_datum(self, data, input_reader, ctx, transient_shard_state):
            logging.warning("MapReduce is disabled, _process_datum is a no-op")
            return True

        def __return(self, shard_state, tstate, task_directive):
            pass

        def _drop_gracefully(self):
            pass

        def _has_old_request_ended(self, shard_state):
            return False

    class _StubSliceContext:
        """Stub slice context"""
        def incr(self, key, delta=1):
            pass
