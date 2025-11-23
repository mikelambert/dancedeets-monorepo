"""
Compatibility layer for App Engine Testbed.

Provides testing infrastructure that works in both
App Engine Standard (with testbed) and Flexible Environment (without).
"""

import os

# Try to use the real App Engine testbed if available
try:
    from google.appengine.ext import testbed as appengine_testbed
    TESTBED_AVAILABLE = True
except ImportError:
    TESTBED_AVAILABLE = False
    appengine_testbed = None


class MockTaskqueueStub:
    """Mock taskqueue stub for testing without App Engine."""

    def __init__(self):
        self._queues = {}

    def GetTasks(self, queue_name):
        return self._queues.get(queue_name, [])

    def FlushQueue(self, queue_name):
        self._queues[queue_name] = []

    def add_task(self, queue_name, task):
        if queue_name not in self._queues:
            self._queues[queue_name] = []
        self._queues[queue_name].append(task)


class Testbed:
    """Mock Testbed for testing in Flexible Environment."""

    TASKQUEUE_SERVICE_NAME = 'taskqueue'

    def __init__(self):
        self._stubs = {}
        self._env_vars = {}
        self._original_env = {}

    def activate(self):
        """Activate the testbed."""
        pass

    def deactivate(self):
        """Deactivate the testbed."""
        # Restore environment variables
        for key, value in self._original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def init_blobstore_stub(self):
        """Initialize blobstore stub (no-op in Flexible)."""
        pass

    def init_datastore_v3_stub(self):
        """Initialize datastore stub (no-op, using Cloud NDB)."""
        pass

    def init_mail_stub(self):
        """Initialize mail stub (no-op in Flexible)."""
        pass

    def init_memcache_stub(self):
        """Initialize memcache stub (no-op, using memcache wrapper)."""
        pass

    def init_search_stub(self):
        """Initialize search stub (no-op, using search_compat)."""
        pass

    def init_taskqueue_stub(self, root_path='.'):
        """Initialize taskqueue stub."""
        self._stubs[self.TASKQUEUE_SERVICE_NAME] = MockTaskqueueStub()

    def init_urlfetch_stub(self):
        """Initialize urlfetch stub (no-op, using requests)."""
        pass

    def get_stub(self, service_name):
        """Get a stub by service name."""
        return self._stubs.get(service_name)

    def setup_env(self, overwrite=False, **kwargs):
        """Set up environment variables."""
        for key, value in kwargs.items():
            if key not in self._original_env:
                self._original_env[key] = os.environ.get(key)
            os.environ[key] = value


# Service name constant
TASKQUEUE_SERVICE_NAME = 'taskqueue'


# If the real testbed is available, use it
if TESTBED_AVAILABLE:
    Testbed = appengine_testbed.Testbed
    TASKQUEUE_SERVICE_NAME = appengine_testbed.TASKQUEUE_SERVICE_NAME
