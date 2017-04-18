import re
import urllib
import webapp2


class HostRoute(webapp2.BaseRoute):
    """A route that is compatible with webapp's routing mechanism.

    URI building is not implemented as webapp has rudimentar support for it,
    and this is the most unknown webapp feature anyway.
    """

    def __init__(self, host, template, handler=None, name=None, build_only=False):
        super(HostRoute, self).__init__(template, handler, name, build_only)
        self.host = host

    @webapp2.cached_property
    def regex(self):
        """Lazy regex compiler."""
        if not self.template.startswith('^'):
            self.template = '^' + self.template

        if not self.template.endswith('$'):
            self.template += '$'

        return re.compile(self.template)

    def match(self, request):
        """Matches this route against the current request.

        .. seealso:: :meth:`BaseRoute.match`.
        """
        # We fetch get_main_hostname dynamically at match-time,
        # to ensure we get the latest self.prod_mode, which may have changed
        route_host = self.host
        request_host = request.host.split(':')[0]
        if request_host.endswith(route_host):
            match = self.regex.match(urllib.unquote(request.path))
            if match:
                return self, match.groups(), {}

    def __repr__(self):
        return '<HostRoute(%r, %r)>' % (self.template, self.handler)


class _DDApplication(webapp2.WSGIApplication):

    def route(self, *args, **kwargs):
        def wrapper(func):
            # Do we want to extend this to full Routes someday?
            # Won't work with batched_mapperworker's slurp-all-but-pass-no-args approach, so need bwcompat
            self.router.add(HostRoute('dancedeets.com', handler=func, *args, **kwargs))
            return func
        return wrapper

    def short_route(self, *args, **kwargs):
        def wrapper(func):
            # Do we want to extend this to full Routes someday?
            # Won't work with batched_mapperworker's slurp-all-but-pass-no-args approach, so need bwcompat
            self.router.add(HostRoute('dd.events', handler=func, *args, **kwargs))
            return func
        return wrapper

app = _DDApplication()
route = app.route
short_route = app.short_route
