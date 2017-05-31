import objgraph
import logging
import random
import StringIO
import sys

NO_LEAK_TYPES = ['MultiDict', 'HTTPAdapter', 'DBEvent', 'Future', 'Context', 'EventLoop', 'google.appengine.datastore.datastore_rpc.Connection']

def gc_debug_diff(since, peak_stats={}, hide_growth=False):
    sio = StringIO.StringIO()
    objgraph.show_growth(limit=0, shortnames=False, peak_stats=peak_stats, file=sio)
    result = sio.getvalue()
    if not hide_growth:
        logging.info("Show Growth since running %s", since)
        for x in result.strip().split('\n')[:200]:
            logging.info(":: %s" % x)
    return result

def gc_debug_backtraces(magictype=None, count=1):
    all_objects = list(objgraph.by_type(magictype))
    sio = StringIO.StringIO()
    objgraph.show_backrefs(all_objects[:count], max_depth=10, shortnames=False, output=sio)
    #objgraph.show_chain(*chains, output=sio2)
    logging.info("%s", sio.getvalue())

def leak_middleware(app):
    def leak_wsgi_wrapper(environ, start_response):
        peak_stats = {}
        gc_debug_diff('request start', peak_stats=peak_stats, hide_growth=True)
        try:
            result = app(environ, start_response)
            if result is not None:
                for value in result:
                    yield value
        finally:
            result = gc_debug_diff('request', peak_stats=peak_stats)
            for obj in NO_LEAK_TYPES:
                if obj in result:
                    gc_debug_backtraces(magictype=obj, count=40)
    return leak_wsgi_wrapper
