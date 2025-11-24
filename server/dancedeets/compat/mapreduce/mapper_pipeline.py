"""Stub for mapreduce.mapper_pipeline"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.mapper_pipeline import *
else:
    class MapperPipeline:
        """Stub MapperPipeline"""
        def __init__(self, *args, **kwargs):
            pass

        def run(self, *args, **kwargs):
            pass

        def start(self, *args, **kwargs):
            pass
