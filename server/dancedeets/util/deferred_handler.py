"""WSGI application handler for deferred tasks.

This replaces google.appengine.ext.deferred.application for handling
deferred task execution from Cloud Tasks.
"""

import logging

from dancedeets.util.deferred import run_deferred


class DeferredHandler:
    """WSGI application that handles deferred task execution."""

    def __call__(self, environ, start_response):
        """Handle a deferred task request."""
        try:
            # Read the request body
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            if content_length:
                body = environ['wsgi.input'].read(content_length)
            else:
                body = b''

            if body:
                # Execute the deferred task
                run_deferred(body)
                start_response('200 OK', [('Content-Type', 'text/plain')])
                return [b'OK']
            else:
                start_response('400 Bad Request', [('Content-Type', 'text/plain')])
                return [b'No payload']

        except Exception as e:
            logging.exception('Error executing deferred task: %s', e)
            # Return 500 so Cloud Tasks will retry
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [str(e).encode('utf-8')]


# WSGI application instance
application = DeferredHandler()
