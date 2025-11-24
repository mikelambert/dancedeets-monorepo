"""Stub for mapreduce.control"""

import logging
from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.control import *
else:
    def start_map(name=None, reader_spec=None, handler_spec=None, output_writer_spec=None,
                  shard_count=None, queue_name=None, mapper_parameters=None, **kwargs):
        """Stub start_map that logs and does nothing"""
        logging.warning("MapReduce is disabled. Skipping start_map: %s", name)
        return None
