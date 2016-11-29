import objgraph
import logging
import random
import StringIO
import sys

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
            for x in result.strip().split('\n'):
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
        random.shuffle(all_objects)
        chains = []
        for obj in all_objects[:count]:
            chains.append(objgraph.find_backref_chain(
                    obj,
                    objgraph.is_proper_module))
        sio2 = StringIO.StringIO()
        objgraph.show_chain(*chains, output=sio2)
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
            for obj in ['MultiDict', 'HTTPAdapter', 'DBEvent', 'Future', 'Context', 'EventLoop', 'google.appengine.datastore.datastore_rpc.Connection', 'OrderedDict']:
                if obj in result:
                    gc_debug_backtraces(magictype=obj, count=5)
    return leak_wsgi_wrapper
