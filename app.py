import webapp2

class _DDApplication(webapp2.WSGIApplication):
    def route(self, *args, **kwargs):
        def wrapper(func):
            # Do we want to extend this to full Routes someday?
            # Won't work with batched_mapperworker's slurp-all-but-pass-no-args approach, so need bwcompat
            self.router.add(webapp2.SimpleRoute(handler=func, *args, **kwargs))
            return func
        return wrapper

app = _DDApplication()
route = app.route
