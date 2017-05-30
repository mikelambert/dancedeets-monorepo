import objgraph
import logging
import random
import StringIO
import sys

NO_LEAK_TYPES = ['MultiDict', 'HTTPAdapter', 'DBEvent', 'Future', 'Context', 'EventLoop', 'google.appengine.datastore.datastore_rpc.Connection']

def gc_debug_diff(since, peak_stats={}, hide_growth=False):
    sio = StringIO.StringIO()
    orig_out = sys.stdout
    result = None
    try:
        sys.stdout = sio
        objgraph.show_growth(limit=0, shortnames=False, peak_stats=peak_stats)
        result = sio.getvalue()
        if not hide_growth:
            logging.info("Show Growth since running %s", since)
            for x in result.strip().split('\n')[:200]:
                logging.info(":: %s" % x)
    finally:
        sys.stdout = orig_out
    return result

def gc_debug_backtraces(magictype=None, count=1):
    sio = StringIO.StringIO()
    orig_out = sys.stdout
    try:
        sys.stdout = sio
        all_objects = list(objgraph.by_type(magictype))
        sio2 = StringIO.StringIO()
        objgraph.show_backrefs(all_objects[:count], max_depth=10, shortnames=False, output=sio2)
        #objgraph.show_chain(*chains, output=sio2)
        logging.info("%s", sio2.getvalue())
    finally:
        sys.stdout = orig_out

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
