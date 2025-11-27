"""Stub for mapreduce.mapreduce_pipeline"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.mapreduce_pipeline import *
else:
    class MapreducePipeline:
        """Stub MapreducePipeline"""
        def __init__(self, *args, **kwargs):
            pass

        def run(self, *args, **kwargs):
            pass

        def start(self, *args, **kwargs):
            pass

    class MapPipeline:
        """Stub MapPipeline"""
        def __init__(self, *args, **kwargs):
            pass
