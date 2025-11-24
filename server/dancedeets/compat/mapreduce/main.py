"""Stub for mapreduce.main"""

import logging
from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.main import *
else:
    import webapp2

    class _StubHandler(webapp2.RequestHandler):
        def get(self):
            logging.warning("MapReduce is disabled")
            self.response.write("MapReduce is disabled")

        def post(self):
            logging.warning("MapReduce is disabled")
            self.response.write("MapReduce is disabled")

    # Create a stub WSGI app
    APP = webapp2.WSGIApplication([
        (r'/mapreduce.*', _StubHandler),
    ], debug=True)
