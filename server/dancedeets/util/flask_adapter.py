"""Flask adapter module for webapp2 compatibility.

This module provides wrapper classes that adapt Flask's request and response
objects to be compatible with webapp2-style request handlers.
"""

import io
from flask import request as flask_request, make_response, Response


class Webapp2Request:
    """Adapter that makes Flask's request look like webapp2's request."""

    def __init__(self, flask_req):
        self._flask_req = flask_req
        self._cookies = dict(flask_req.cookies)
        self._GET = flask_req.args
        self._POST = flask_req.form

    @property
    def method(self):
        return self._flask_req.method

    @property
    def url(self):
        return self._flask_req.url

    @property
    def path(self):
        return self._flask_req.path

    @property
    def host(self):
        return self._flask_req.host

    @property
    def headers(self):
        return self._flask_req.headers

    @property
    def cookies(self):
        return self._cookies

    @property
    def user_agent(self):
        return self._flask_req.user_agent.string

    @property
    def body(self):
        return self._flask_req.get_data()

    @property
    def GET(self):
        return self._GET

    @property
    def POST(self):
        return self._POST

    @property
    def app(self):
        """Return the Flask app (needed for prod_mode check)."""
        return getattr(self, '_app', None)

    def get(self, key, default=''):
        """Get a request parameter (from GET or POST)."""
        return self._flask_req.values.get(key, default)

    def get_all(self, key):
        """Get all values for a request parameter."""
        return self._flask_req.values.getlist(key)


class Webapp2ResponseOut:
    """File-like object for response output."""

    def __init__(self, response):
        self._response = response
        self._output = io.BytesIO()

    def write(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        self._output.write(data)

    def getvalue(self):
        return self._output.getvalue()


class Webapp2Headers(dict):
    """Dict-like object that also supports webapp2's add_header method."""

    def add_header(self, name, value, **params):
        """Add a header with optional parameters (webapp2 compatibility)."""
        # Build header value with parameters
        header_value = value
        for param_name, param_value in params.items():
            if param_value is not None:
                header_value += f'; {param_name}={param_value}'
        self[name] = header_value


class Webapp2Response:
    """Adapter that makes Flask's response look like webapp2's response."""

    def __init__(self):
        self._headers = Webapp2Headers()
        self._status = 200
        self._status_message = 'OK'
        self.out = Webapp2ResponseOut(self)
        self._cookies = []

    @property
    def headers(self):
        return self._headers

    def set_status(self, code, message=None):
        self._status = code
        if message:
            self._status_message = message

    def set_cookie(self, name, value, max_age=None, path='/', domain=None, secure=False, httponly=False):
        self._cookies.append({
            'name': name,
            'value': value,
            'max_age': max_age,
            'path': path,
            'domain': domain,
            'secure': secure,
            'httponly': httponly
        })

    def clear_cookie(self, name, path='/', domain=None):
        self.set_cookie(name, '', max_age=0, path=path, domain=domain)

    def to_flask_response(self):
        """Convert to a Flask Response object."""
        body = self.out.getvalue()
        response = Response(body, status=self._status)

        # Copy headers
        for key, value in self._headers.items():
            response.headers[key] = value

        # Set cookies
        for cookie in self._cookies:
            response.set_cookie(
                cookie['name'],
                cookie['value'],
                max_age=cookie.get('max_age'),
                path=cookie.get('path', '/'),
                domain=cookie.get('domain'),
                secure=cookie.get('secure', False),
                httponly=cookie.get('httponly', False)
            )

        return response


class BaseHandler:
    """Base class for Flask-compatible webapp2-style handlers."""

    def __init__(self):
        self.request = None
        self.response = None
        self._app = None

    def initialize(self, flask_req, app):
        """Initialize the handler with the request and app."""
        self.request = Webapp2Request(flask_req)
        self.request._app = app  # Attach app for prod_mode checks
        self.response = Webapp2Response()
        self._app = app

    def get(self, **kwargs):
        """Handle GET request. Override in subclasses."""
        return self.response.to_flask_response()

    def post(self, **kwargs):
        """Handle POST request. Override in subclasses."""
        return self.get(**kwargs)

    def head(self, **kwargs):
        """Handle HEAD request."""
        return self.get(**kwargs)

    def redirect(self, url, permanent=False, abort=True):
        """Redirect to a URL."""
        from flask import redirect as flask_redirect
        self.response.set_status(301 if permanent else 302)
        self.response.headers['Location'] = url
        if abort:
            # Return the redirect response directly
            return flask_redirect(url, code=301 if permanent else 302)

    def abort(self, code, detail=None):
        """Abort with an error code."""
        from flask import abort as flask_abort
        flask_abort(code, description=detail)
