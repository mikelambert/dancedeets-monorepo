"""
Compatibility layer for Google App Engine Search API.

The App Engine Search API is not available in Flexible Environment.
This module provides a compatibility layer that can be swapped for
a real implementation (Elasticsearch, Cloud Search, etc.) later.

For now, it provides stub implementations that allow the app to run
without the Search API, with reduced search functionality.
"""

import logging
import os


def _is_flexible_environment():
    """Check if running in App Engine Flexible Environment.

    In Flexible Environment:
    - GAE_ENV is 'flex' or 'flexible'
    - GAE_VM is 'true'

    The Search API is only available in Standard Environment.
    """
    gae_env = os.environ.get('GAE_ENV', '')
    gae_vm = os.environ.get('GAE_VM', '')
    return gae_env in ('flex', 'flexible') or gae_vm == 'true'


# The App Engine Search API doesn't work in Flexible Environment.
# Even though the import succeeds (from appengine-python-standard), the actual
# API calls fail with "No api proxy found for service 'search'".
#
# Force SEARCH_AVAILABLE = False to always use the stub implementation.
# This is necessary because:
# 1. Environment detection at import time may not work reliably
# 2. GAE Flex definitely doesn't support the Search API
# 3. The stub implementation gracefully returns empty results
#
# If you need real search, implement Elasticsearch or Cloud Search instead.
SEARCH_AVAILABLE = False
appengine_search = None
logging.info("Using Search API stub implementation (Search API not available in Flexible Environment)")


class SearchError(Exception):
    """Base exception for search errors."""
    pass


class QueryError(SearchError):
    """Exception for invalid queries."""
    pass


# Constants that mirror the App Engine Search API
MAXIMUM_DOCUMENTS_RETURNED_PER_SEARCH = 1000
MAXIMUM_DOCUMENTS_PER_PUT_REQUEST = 200


class TextField:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class NumberField:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class DateField:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Document:
    def __init__(self, doc_id=None, fields=None, rank=None, language=None):
        self.doc_id = doc_id
        self._fields = {f.name: f for f in (fields or [])}
        self.rank = rank or 0
        self.language = language

    def field(self, name):
        return self._fields.get(name)


class QueryOptions:
    def __init__(self, limit=None, returned_fields=None, **kwargs):
        self.limit = limit or MAXIMUM_DOCUMENTS_RETURNED_PER_SEARCH
        self.returned_fields = returned_fields or []


class Query:
    def __init__(self, query_string=None, options=None):
        self.query_string = query_string
        self.options = options


class SearchResults:
    def __init__(self, results=None):
        self.results = results or []


class Index:
    """Stub Index implementation.

    In production, this should be replaced with a real search backend
    like Elasticsearch or Cloud Search.
    """
    _indexes = {}  # In-memory storage for development

    def __init__(self, name):
        self.name = name
        if name not in Index._indexes:
            Index._indexes[name] = {}

    def put(self, documents):
        """Add documents to the index."""
        if not isinstance(documents, list):
            documents = [documents]
        for doc in documents:
            Index._indexes[self.name][doc.doc_id] = doc
        logging.info("Search index %s: added %d documents", self.name, len(documents))

    def delete(self, doc_ids):
        """Delete documents from the index."""
        if not isinstance(doc_ids, list):
            doc_ids = [doc_ids]
        for doc_id in doc_ids:
            if doc_id in Index._indexes[self.name]:
                del Index._indexes[self.name][doc_id]
        logging.info("Search index %s: deleted %d documents", self.name, len(doc_ids))

    def search(self, query):
        """Search the index.

        Note: This is a stub implementation that returns all documents.
        A real implementation should parse the query and filter results.
        """
        logging.warning("Search API stub: returning empty results for query: %s", query.query_string)
        # Return empty results - the app should fall back to database queries
        return SearchResults(results=[])

    def get_range(self, ids_only=False, start_id=None, include_start_object=True, limit=1000):
        """Get a range of documents from the index."""
        docs = list(Index._indexes[self.name].values())
        if start_id:
            docs = [d for d in docs if d.doc_id > start_id]
        docs = docs[:limit]
        if ids_only:
            return [type('obj', (object,), {'doc_id': d.doc_id})() for d in docs]
        return docs


def _CheckQuery(query_string):
    """Validate a query string.

    This is a stub that always passes validation.
    """
    pass


# If the real Search API is available, use it
if SEARCH_AVAILABLE:
    # Re-export everything from the real module
    TextField = appengine_search.TextField
    NumberField = appengine_search.NumberField
    DateField = appengine_search.DateField
    Document = appengine_search.Document
    Query = appengine_search.Query
    QueryOptions = appengine_search.QueryOptions
    Index = appengine_search.Index
    QueryError = appengine_search.QueryError
    MAXIMUM_DOCUMENTS_RETURNED_PER_SEARCH = appengine_search.MAXIMUM_DOCUMENTS_RETURNED_PER_SEARCH
    MAXIMUM_DOCUMENTS_PER_PUT_REQUEST = appengine_search.MAXIMUM_DOCUMENTS_PER_PUT_REQUEST
    # _CheckQuery is a private API that may not exist in appengine-python-standard
    if hasattr(appengine_search, '_CheckQuery'):
        _CheckQuery = appengine_search._CheckQuery
    # Otherwise use our local stub _CheckQuery defined above
