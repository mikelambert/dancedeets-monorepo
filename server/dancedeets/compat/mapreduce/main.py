"""Stub for mapreduce.main"""

import logging
from dancedeets.compat import LEGACY_APIS_ENABLED

if LEGACY_APIS_ENABLED:
    from mapreduce.main import *
else:
    # Stub WSGI app - MapReduce is disabled in Flex environment
    def APP(environ, start_response):
        logging.warning("MapReduce is disabled")
        status = '503 Service Unavailable'
        response_headers = [('Content-Type', 'text/plain')]
        start_response(status, response_headers)
        return [b'MapReduce is disabled']
