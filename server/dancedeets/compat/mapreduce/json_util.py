"""Stub for mapreduce.json_util"""

from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.json_util import *
else:
    import json
    from google.appengine.ext import db

    class JsonMixin:
        """Stub JsonMixin"""
        def to_json(self):
            return json.dumps(self.__dict__)

        @classmethod
        def from_json(cls, json_str):
            return cls()

    class JsonProperty(db.TextProperty):
        """A property that stores a JSON-serializable Python object.

        This is a db.Property (not ndb) that stores Python objects as JSON text.
        Used for the old db.Model API in thing_db.py.
        """
        def __init__(self, data_type=dict, indexed=False, **kwargs):
            # data_type is accepted but not enforced in the stub
            super(JsonProperty, self).__init__(indexed=indexed, **kwargs)

        def get_value_for_datastore(self, model_instance):
            """Serialize the Python object to JSON string for storage."""
            value = super(JsonProperty, self).get_value_for_datastore(model_instance)
            if value is None:
                return None
            return json.dumps(value)

        def make_value_from_datastore(self, value):
            """Deserialize JSON string back to Python object."""
            if value is None:
                return None
            return json.loads(value)

        def validate(self, value):
            """Allow any JSON-serializable value."""
            return value
