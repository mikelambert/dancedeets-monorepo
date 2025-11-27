"""Stub for pipeline.handlers"""

import logging
from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from pipeline.handlers import *
else:
    # Stub WSGI app - Pipeline is disabled in Flex environment
    def _APP(environ, start_response):
        logging.warning("Pipeline is disabled")
        status = '503 Service Unavailable'
        response_headers = [('Content-Type', 'text/plain')]
        start_response(status, response_headers)
        return [b'Pipeline is disabled']
