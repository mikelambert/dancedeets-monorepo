"""DanceDeets Flask application with webapp2-compatible routing.

This module provides a Flask application with decorators that mimic
the webapp2 routing interface for backwards compatibility.
"""

import functools
import logging
import re
import urllib.parse

from flask import Flask, request as flask_request, g


class _DDApplication(Flask):
    """Flask application with webapp2-compatible routing decorators."""

    def __init__(self, *args, **kwargs):
        super().__init__(__name__, *args, **kwargs)
        self.prod_mode = False
        self._host_routes = []

    def route(self, template, **kwargs):
        """Decorator to register a route for dancedeets.com hosts.

        This maintains compatibility with the webapp2-style routing.
        """
        host_pattern = r'dancedeets\.com$|dancedeets-hrd\.appspot\.com$|localhost'

        def decorator(handler_class):
            return self._register_route(host_pattern, template, handler_class, **kwargs)

        return decorator

    def short_route(self, template, **kwargs):
        """Decorator to register a route for dd.events hosts."""
        host_pattern = r'dd\.events$'

        def decorator(handler_class):
            return self._register_route(host_pattern, template, handler_class, **kwargs)

        return decorator

    def bio_route(self, template, **kwargs):
        """Decorator to register a route for dancer.bio hosts."""
        host_pattern = r'dancer?\.bio$'

        def decorator(handler_class):
            return self._register_route(host_pattern, template, handler_class, **kwargs)

        return decorator

    def _register_route(self, host_pattern, template, handler_class, **kwargs):
        """Register a route with host-based matching."""
        # Normalize template to Flask format
        # webapp2 uses regex groups, Flask uses <variable> syntax
        flask_template = self._convert_template(template)

        # Create unique endpoint name
        endpoint = f"{handler_class.__name__}_{len(self._host_routes)}"

        # Store host pattern for matching
        self._host_routes.append({
            'host_pattern': re.compile(host_pattern),
            'endpoint': endpoint,
            'handler_class': handler_class,
        })

        # Create view function that instantiates the handler class
        @functools.wraps(handler_class)
        def view_func(**url_kwargs):
            # Check host pattern
            request_host = flask_request.host.split(':')[0]
            for route_info in self._host_routes:
                if route_info['endpoint'] == endpoint:
                    if not route_info['host_pattern'].search(request_host):
                        return 'Not Found', 404
                    break

            # Instantiate handler and call appropriate method
            handler = handler_class()
            handler.initialize(flask_request, self)

            method = flask_request.method.lower()
            method_func = getattr(handler, method, None)
            if method_func is None:
                method_func = getattr(handler, 'get', None)

            if method_func:
                return method_func(**url_kwargs)
            else:
                return 'Method Not Allowed', 405

        # Register with Flask
        methods = kwargs.pop('methods', ['GET', 'POST', 'HEAD'])
        self.add_url_rule(flask_template, endpoint=endpoint, view_func=view_func, methods=methods)

        return handler_class

    def _convert_template(self, template):
        """Convert webapp2/regex route template to Flask format."""
        # Remove regex anchors
        template = template.lstrip('^').rstrip('$')

        # Convert regex groups to Flask variables
        # (\d+) or ([^/]+) -> <path:var> or <var>
        # Named groups (?P<name>pattern) -> <name>

        # Handle named groups first
        def replace_named_group(match):
            name = match.group(1)
            return f'<{name}>'

        template = re.sub(r'\(\?P<(\w+)>[^)]+\)', replace_named_group, template)

        # Handle unnamed groups (assign sequential names)
        group_count = [0]

        def replace_group(match):
            group_count[0] += 1
            return f'<arg{group_count[0]}>'

        template = re.sub(r'\([^)]+\)', replace_group, template)

        # Remove remaining regex syntax
        template = template.replace('.*', '')
        template = template.replace('.+', '')
        template = re.sub(r'\?', '', template)

        return template


# Create the application instance
app = _DDApplication()

# Export decorators for backwards compatibility
route = app.route
short_route = app.short_route
bio_route = app.bio_route
