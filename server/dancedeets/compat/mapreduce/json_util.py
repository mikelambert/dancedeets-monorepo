"""Stub for mapreduce.json_util"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.json_util import *
else:
    import json

    class JsonMixin:
        """Stub JsonMixin"""
        def to_json(self):
            return json.dumps(self.__dict__)

        @classmethod
        def from_json(cls, json_str):
            return cls()
