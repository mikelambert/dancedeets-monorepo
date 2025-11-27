"""Task queue operations using Google Cloud Tasks.

This module provides a compatibility layer for migrating from
google.appengine.api.taskqueue to Google Cloud Tasks.

Usage:
    from dancedeets.util import taskqueue

    # Add a task to a queue
    taskqueue.add(url='/tasks/my_task', method='POST', queue_name='slow-queue')
"""

import logging
import os
import urllib.parse

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

# Cloud Tasks client (singleton)
_client = None

# Project and location configuration
PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT') or os.environ.get('GAE_APPLICATION', '').replace('s~', '')
LOCATION = os.environ.get('CLOUD_TASKS_LOCATION', 'us-central1')

# Default service for task execution
DEFAULT_SERVICE = os.environ.get('GAE_SERVICE', 'default')

# Constants for backwards compatibility
DEFAULT_APP_VERSION = DEFAULT_SERVICE


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


def _get_service_url(target=None):
    """Get the base URL for the service."""
    service = target or DEFAULT_SERVICE
    if os.environ.get('GAE_ENV') == 'standard':
        return f"https://{service}-dot-{PROJECT_ID}.appspot.com"
    elif PROJECT_ID:
        return f"https://{service}-dot-{PROJECT_ID}.appspot.com"
    else:
        # Local development
        return "http://localhost:8080"


class Task:
    """Represents a Cloud Task for backwards compatibility."""

    def __init__(self, name=None, url=None, method='POST', payload=None,
                 params=None, headers=None, countdown=None, eta=None,
                 target=None, retry_options=None):
        self.name = name
        self.url = url
        self.method = method.upper()
        self.payload = payload
        self.params = params or {}
        self.headers = headers or {}
        self.countdown = countdown
        self.eta = eta
        self.target = target
        self.retry_options = retry_options


def add(url=None, method='POST', payload=None, params=None, headers=None,
        countdown=None, eta=None, name=None, target=None, queue_name='default',
        retry_options=None, transactional=False, **kwargs):
    """Add a task to a Cloud Tasks queue.

    Args:
        url: The URL to call
        method: HTTP method (GET, POST, etc.)
        payload: Request body for POST/PUT requests
        params: URL parameters (for GET requests or appended to URL)
        headers: HTTP headers
        countdown: Seconds to wait before executing (optional)
        eta: Absolute time to execute (datetime, optional)
        name: Task name (optional, auto-generated if not provided)
        target: Target service (optional)
        queue_name: The queue name (default: 'default')
        retry_options: Not directly supported, ignored
        transactional: Not supported in Cloud Tasks, ignored
        **kwargs: Additional arguments (ignored for compatibility)

    Returns:
        A Task object representing the created task
    """
    client = _get_client()
    queue_path = _get_queue_path(queue_name)

    # Build the full URL
    service_url = _get_service_url(target)
    if params:
        url_params = urllib.parse.urlencode(params)
        if '?' in url:
            full_url = f"{service_url}{url}&{url_params}"
        else:
            full_url = f"{service_url}{url}?{url_params}"
    else:
        full_url = f"{service_url}{url}"

    logging.info('CLOUD_TASK_ADD: url=%s, method=%s, queue=%s', full_url, method, queue_name)

    # Build headers
    task_headers = {'Content-Type': 'application/octet-stream'}
    if headers:
        task_headers.update(headers)

    # Build the task
    http_method = getattr(tasks_v2.HttpMethod, method.upper(), tasks_v2.HttpMethod.POST)
    task = {
        'http_request': {
            'http_method': http_method,
            'url': full_url,
            'headers': task_headers,
        }
    }

    # Add body for POST/PUT requests
    if payload is not None:
        if isinstance(payload, str):
            task['http_request']['body'] = payload.encode('utf-8')
        else:
            task['http_request']['body'] = payload

    # Add OIDC token for authentication
    if PROJECT_ID:
        service_account = f"{PROJECT_ID}@appspot.gserviceaccount.com"
        task['http_request']['oidc_token'] = {
            'service_account_email': service_account,
        }

    # Set schedule time if countdown or eta provided
    if countdown is not None:
        import datetime
        schedule_time = timestamp_pb2.Timestamp()
        schedule_time.FromDatetime(
            datetime.datetime.utcnow() + datetime.timedelta(seconds=countdown)
        )
        task['schedule_time'] = schedule_time
    elif eta is not None:
        schedule_time = timestamp_pb2.Timestamp()
        schedule_time.FromDatetime(eta)
        task['schedule_time'] = schedule_time

    # Set task name if provided
    if name:
        task['name'] = f"{queue_path}/tasks/{name}"

    try:
        response = client.create_task(parent=queue_path, task=task)
        logging.info('Created task: %s', response.name)

        # Return a Task object for backwards compatibility
        result = Task(
            name=response.name,
            url=url,
            method=method,
            payload=payload,
            params=params,
            headers=headers,
            countdown=countdown,
            eta=eta,
            target=target
        )
        return result
    except Exception as e:
        logging.error('Error creating task: %s', e)
        raise


class Queue:
    """Represents a Cloud Tasks queue for backwards compatibility."""

    def __init__(self, name='default'):
        self.name = name

    def add(self, task=None, **kwargs):
        """Add a task to this queue."""
        if task is not None:
            return add(
                url=task.url,
                method=task.method,
                payload=task.payload,
                params=task.params,
                headers=task.headers,
                countdown=task.countdown,
                eta=task.eta,
                name=task.name,
                target=task.target,
                queue_name=self.name,
                retry_options=task.retry_options
            )
        else:
            return add(queue_name=self.name, **kwargs)

    def purge(self):
        """Purge all tasks from the queue."""
        client = _get_client()
        queue_path = _get_queue_path(self.name)
        try:
            client.purge_queue(name=queue_path)
            logging.info('Purged queue: %s', self.name)
        except Exception as e:
            logging.error('Error purging queue %s: %s', self.name, e)
            raise


# For backwards compatibility
__all__ = ['add', 'Task', 'Queue', 'DEFAULT_APP_VERSION']
