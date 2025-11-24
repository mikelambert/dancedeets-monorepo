"""Stub for pipeline.handlers"""

import logging
from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from pipeline.handlers import *
else:
    import webapp2

    class _StubHandler(webapp2.RequestHandler):
        def get(self):
            logging.warning("Pipeline is disabled")
            self.response.write("Pipeline is disabled")

        def post(self):
            logging.warning("Pipeline is disabled")
            self.response.write("Pipeline is disabled")

    # Stub WSGI app for pipeline handlers
    _APP = webapp2.WSGIApplication([
        (r'/_pipeline.*', _StubHandler),
    ], debug=True)
