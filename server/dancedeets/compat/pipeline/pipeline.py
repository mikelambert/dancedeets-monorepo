"""Stub for pipeline.pipeline"""

import logging
from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from pipeline.pipeline import *
else:
    class Pipeline:
        """Stub Pipeline base class"""
        def __init__(self, *args, **kwargs):
            pass

        def run(self, *args, **kwargs):
            logging.warning("Pipeline is disabled")
            pass

        def start(self, *args, **kwargs):
            logging.warning("Pipeline is disabled")
            pass

        @classmethod
        def from_id(cls, pipeline_id):
            return None

    class PipelineFuture:
        """Stub PipelineFuture"""
        def __init__(self, *args, **kwargs):
            pass

    class After:
        """Stub After"""
        def __init__(self, *args, **kwargs):
            pass

    class InOrder:
        """Stub InOrder context manager"""
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass
