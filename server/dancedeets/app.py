"""DanceDeets Flask application with webapp2-compatible routing.

This module provides a Flask application with decorators that mimic
the webapp2 routing interface for backwards compatibility.
"""

import functools
import inspect
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

            # Check if initialize() indicated we should skip the handler (e.g., due to redirect)
            if hasattr(handler, 'run_handler') and not handler.run_handler:
                return handler.response.to_flask_response()

            method = flask_request.method.lower()
            method_func = getattr(handler, method, None)
            if method_func is None:
                method_func = getattr(handler, 'get', None)
            # Also check for 'handle' method (used by some handlers)
            if method_func is None:
                method_func = getattr(handler, 'handle', None)

            if method_func:
                # Map arg1, arg2, etc. to the actual parameter names expected by the method
                # This provides compatibility with webapp2-style handlers that use positional args
                mapped_kwargs = self._map_url_kwargs_to_method_params(method_func, url_kwargs)
                result = method_func(**mapped_kwargs)
                # webapp2-style handlers return None but write to self.response
                # Flask requires a return value, so fall back to the response object
                if result is None:
                    return handler.response.to_flask_response()
                return result
            else:
                return 'Method Not Allowed', 405

        # Register with Flask
        methods = kwargs.pop('methods', ['GET', 'POST', 'HEAD'])
        self.add_url_rule(flask_template, endpoint=endpoint, view_func=view_func, methods=methods)

        return handler_class

    def _map_url_kwargs_to_method_params(self, method_func, url_kwargs):
        """Map Flask url_kwargs (arg1, arg2, etc.) to actual method parameter names.

        This provides backwards compatibility with webapp2-style handlers that
        expect positional arguments in their get/post methods.
        """
        if not url_kwargs:
            return {}

        # Get the method's parameter names (skip 'self')
        try:
            sig = inspect.signature(method_func)
            param_names = [p for p in sig.parameters.keys() if p != 'self']
        except (ValueError, TypeError):
            return url_kwargs

        # If the method already uses arg1, arg2, etc., just pass through
        if param_names and param_names[0].startswith('arg'):
            return url_kwargs

        # Map arg1 -> first param, arg2 -> second param, etc.
        mapped_kwargs = {}
        for key, value in url_kwargs.items():
            if key.startswith('arg') and key[3:].isdigit():
                arg_index = int(key[3:]) - 1  # arg1 -> index 0
                if arg_index < len(param_names):
                    mapped_kwargs[param_names[arg_index]] = value
                else:
                    mapped_kwargs[key] = value
            else:
                mapped_kwargs[key] = value

        return mapped_kwargs

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

        # Handle non-capturing groups with optional content (?:...)?
        # These become optional path segments - we convert the inner capturing group
        # and remove the non-capturing wrapper
        def replace_non_capturing_optional(match):
            inner = match.group(1)
            # Replace any capturing groups inside
            inner_count = [0]
            def replace_inner(m):
                inner_count[0] += 1
                return f'<arg{inner_count[0]}>'
            inner = re.sub(r'\([^)]+\)', replace_inner, inner)
            # Remove regex syntax from inner content
            inner = inner.replace('/?', '')
            inner = re.sub(r'\?', '', inner)
            return inner if inner_count[0] > 0 else ''

        # Match (?:content)? patterns (non-capturing optional groups)
        template = re.sub(r'\(\?:([^)]+)\)\?', replace_non_capturing_optional, template)

        # Handle remaining non-capturing groups (?:...) without the optional marker
        template = re.sub(r'\(\?:([^)]+)\)', r'\1', template)

        # Handle unnamed capturing groups (assign sequential names)
        group_count = [0]

        def replace_group(match):
            group_count[0] += 1
            group_content = match.group(0)
            # Check if the group contains a literal '/' outside of character classes
            # e.g., ([^/]+/[^/]+) has a literal '/' but ([^/]+) does not
            # Remove character classes like [^/] before checking for '/'
            content_without_char_classes = re.sub(r'\[[^\]]*\]', '', group_content)
            if '/' in content_without_char_classes:
                return f'<path:arg{group_count[0]}>'
            return f'<arg{group_count[0]}>'

        template = re.sub(r'\([^)]+\)', replace_group, template)

        # Remove remaining regex syntax
        template = template.replace('.*', '')
        template = template.replace('.+', '')
        template = template.replace('/?', '')  # optional trailing slash
        template = re.sub(r'\?', '', template)

        # Ensure template starts with /
        if not template.startswith('/'):
            template = '/' + template

        return template


# Create the application instance
app = _DDApplication()


# Health check endpoint for App Engine Flexible
# This must be a simple direct route, not using the webapp2-compat decorators
def _health_check():
    """Health check endpoint for App Engine Flexible."""
    return 'ok', 200


app.add_url_rule('/_ah/health', 'health_check', _health_check, methods=['GET'])


# Export decorators for backwards compatibility
route = app.route
short_route = app.short_route
bio_route = app.bio_route
