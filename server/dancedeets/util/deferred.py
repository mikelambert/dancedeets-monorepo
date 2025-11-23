"""Deferred task execution using Google Cloud Tasks.

This module provides a compatibility layer for migrating from
google.appengine.ext.deferred to Google Cloud Tasks.

Usage:
    from dancedeets.util import deferred

    # Defer a function call
    deferred.defer(my_function, arg1, arg2, _queue='slow-queue')
"""

import json
import logging
import os
import pickle
import base64

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

# Cloud Tasks client (singleton)
_client = None

# Project and location configuration
PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT') or os.environ.get('GAE_APPLICATION', '').replace('s~', '')
LOCATION = os.environ.get('CLOUD_TASKS_LOCATION', 'us-central1')

# Default service for task execution
DEFAULT_SERVICE = os.environ.get('GAE_SERVICE', 'default')


def _get_client():
    """Get or create the Cloud Tasks client."""
    global _client
    if _client is None:
        _client = tasks_v2.CloudTasksClient()
    return _client


def _get_queue_path(queue_name):
    """Get the full queue path for Cloud Tasks."""
    client = _get_client()
    return client.queue_path(PROJECT_ID, LOCATION, queue_name)


def _get_service_url():
    """Get the base URL for the service."""
    if os.environ.get('GAE_ENV') == 'standard':
        return f"https://{DEFAULT_SERVICE}-dot-{PROJECT_ID}.appspot.com"
    elif PROJECT_ID:
        return f"https://{DEFAULT_SERVICE}-dot-{PROJECT_ID}.appspot.com"
    else:
        # Local development
        return "http://localhost:8080"


def defer(func, *args, _queue='default', _countdown=None, _eta=None, _name=None,
          _target=None, _url=None, _transactional=False, _retry_options=None,
          **kwargs):
    """Defer a function call to be executed by a Cloud Task.

    Args:
        func: The function to call
        *args: Positional arguments for the function
        _queue: The queue name (default: 'default')
        _countdown: Seconds to wait before executing (optional)
        _eta: Absolute time to execute (datetime, optional)
        _name: Task name (optional, auto-generated if not provided)
        _target: Target service (optional)
        _url: URL to call (default: /_ah/queue/deferred)
        _transactional: Not supported in Cloud Tasks, ignored
        _retry_options: Not directly supported, ignored
        **kwargs: Keyword arguments for the function

    Returns:
        The created task name
    """
    client = _get_client()
    queue_path = _get_queue_path(_queue)

    # Serialize the function call using pickle (same as App Engine deferred)
    payload = pickle.dumps((func, args, kwargs))
    encoded_payload = base64.b64encode(payload).decode('utf-8')

    # Build the task URL
    if _url is None:
        _url = '/_ah/queue/deferred'

    service_url = _get_service_url()
    if _target:
        # Override the service in the URL
        service_url = service_url.replace(f"{DEFAULT_SERVICE}-dot-", f"{_target}-dot-")

    full_url = f"{service_url}{_url}"

    # Build the task
    task = {
        'http_request': {
            'http_method': tasks_v2.HttpMethod.POST,
            'url': full_url,
            'body': encoded_payload.encode(),
            'headers': {
                'Content-Type': 'application/octet-stream',
            },
        }
    }

    # Add OIDC token for authentication
    if PROJECT_ID:
        service_account = f"{PROJECT_ID}@appspot.gserviceaccount.com"
        task['http_request']['oidc_token'] = {
            'service_account_email': service_account,
        }

    # Set schedule time if countdown or eta provided
    if _countdown is not None:
        import datetime
        schedule_time = timestamp_pb2.Timestamp()
        schedule_time.FromDatetime(
            datetime.datetime.utcnow() + datetime.timedelta(seconds=_countdown)
        )
        task['schedule_time'] = schedule_time
    elif _eta is not None:
        schedule_time = timestamp_pb2.Timestamp()
        schedule_time.FromDatetime(_eta)
        task['schedule_time'] = schedule_time

    # Set task name if provided
    if _name:
        task['name'] = f"{queue_path}/tasks/{_name}"

    try:
        response = client.create_task(parent=queue_path, task=task)
        logging.info('Created deferred task: %s', response.name)
        return response.name
    except Exception as e:
        logging.error('Error creating deferred task: %s', e)
        raise


def run_deferred(payload):
    """Execute a deferred task from its payload.

    This should be called from the /_ah/queue/deferred handler.

    Args:
        payload: The base64-encoded pickled function call
    """
    try:
        decoded = base64.b64decode(payload)
        func, args, kwargs = pickle.loads(decoded)
        func(*args, **kwargs)
    except Exception as e:
        logging.exception('Error running deferred task: %s', e)
        raise


# For backwards compatibility with imports like:
# from dancedeets.util.deferred import defer
__all__ = ['defer', 'run_deferred']
