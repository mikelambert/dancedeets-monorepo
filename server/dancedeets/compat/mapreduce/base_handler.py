"""Stub for mapreduce.base_handler"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.base_handler import *
else:
    class PipelineBase:
        """Stub PipelineBase"""
        def run(self, *args, **kwargs):
            pass

        def start(self, *args, **kwargs):
            pass
