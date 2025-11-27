"""NDB Client wrapper for Google Cloud NDB.

This module provides a compatibility layer for migrating from
google.appengine.ext.ndb to google.cloud.ndb.

Usage:
    from dancedeets.util.ndb_client import ndb, get_ndb_context

    # For WSGI applications, use the context middleware
    application = ndb_wsgi_middleware(application)

    # For background tasks or scripts, use context manager
    with get_ndb_context():
        entity = MyModel.get_by_id('key')
"""

import functools
import logging
import os

# Import Cloud NDB
from google.cloud import ndb

# Create the NDB client (singleton)
_client = None


def get_ndb_client():
    """Get or create the NDB client singleton."""
    global _client
    if _client is None:
        project = os.environ.get('GOOGLE_CLOUD_PROJECT') or os.environ.get('GAE_APPLICATION')
        if project:
            _client = ndb.Client(project=project)
        else:
            _client = ndb.Client()
        logging.info('Initialized NDB client for project: %s', project)
    return _client


def get_ndb_context():
    """Get an NDB context for use in context managers.

    Usage:
        with get_ndb_context():
            entity = MyModel.get_by_id('key')
    """
    return get_ndb_client().context()


def ndb_context(func):
    """Decorator to wrap a function with NDB context.

    Usage:
        @ndb_context
        def my_function():
            entity = MyModel.get_by_id('key')
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with get_ndb_context():
            return func(*args, **kwargs)
    return wrapper


class NDBContextMiddleware:
    """WSGI middleware that provides NDB context for each request.

    Usage:
        application = NDBContextMiddleware(application)
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        with get_ndb_context():
            return self.app(environ, start_response)


def ndb_wsgi_middleware(app):
    """Wrap a WSGI application with NDB context middleware."""
    return NDBContextMiddleware(app)


# Re-export commonly used NDB classes and functions for convenience
# This allows: from dancedeets.util.ndb_client import ndb, Model, Key, etc.
Model = ndb.Model
Key = ndb.Key
StringProperty = ndb.StringProperty
TextProperty = ndb.TextProperty
IntegerProperty = ndb.IntegerProperty
FloatProperty = ndb.FloatProperty
BooleanProperty = ndb.BooleanProperty
DateTimeProperty = ndb.DateTimeProperty
DateProperty = ndb.DateProperty
TimeProperty = ndb.TimeProperty
BlobProperty = ndb.BlobProperty
JsonProperty = ndb.JsonProperty
GeoPtProperty = ndb.GeoPtProperty
KeyProperty = ndb.KeyProperty
StructuredProperty = ndb.StructuredProperty
LocalStructuredProperty = ndb.LocalStructuredProperty
ComputedProperty = ndb.ComputedProperty
GenericProperty = ndb.GenericProperty
PickleProperty = ndb.PickleProperty
Expando = ndb.Expando

# Query-related
Query = ndb.Query
QueryOptions = ndb.QueryOptions
AND = ndb.AND
OR = ndb.OR

# Transaction support
transaction = ndb.transaction
transaction_async = ndb.transaction_async
transactional = ndb.transactional
non_transactional = ndb.non_transactional

# Context
Context = ndb.Context
