"""Stub for mapreduce.pipeline_base"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.pipeline_base import *
else:
    class PipelineBase:
        """Stub PipelineBase"""
        def run(self, *args, **kwargs):
            pass

        def start(self, *args, **kwargs):
            pass
