def gc_debug_diff(since, peak_stats={}, hide_growth=False):
    import objgraph
    import StringIO
    import sys
    import logging
    sio = StringIO.StringIO()
    orig_out = sys.stdout
    result = None
    try:
        sys.stdout = sio
        objgraph.show_growth(limit=20, shortnames=False, peak_stats=peak_stats)
        result = sio.getvalue()
        if not hide_growth:
            logging.info("Show Growth since running %s", since)
            for x in result.strip().split('\n'):
                logging.info(":: %s" % x)
    finally:
        sys.stdout = orig_out
    return result

def gc_debug_backtraces(magictype=None, count=1):
    import objgraph
    import logging
    import random
    import StringIO
    import sys
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
    except Exception:
      raise
    finally:
      gc_debug_diff('request', count=20, peak_stats=peak_stats)
  return leak_wsgi_wrapper

def webapp_add_wsgi_middleware(app):
    #from google.appengine.ext.appstats import recording
    #app = recording.appstats_wsgi_middleware(app)
    app = leak_middleware(app)
    return app

# We don't need such real-time statistics (normally 1 second) on the mapreduce job.
# More of an optimization to save on the associated database Get/Put every second.
mapreduce__CONTROLLER_PERIOD_SEC = 5

appstats_MAX_STACK = 25
appstats_MAX_REPR = 100
appstats_MAX_LOCALS = 5

appstats_RECORD_FRACTION = 1.0

appstats_DATASTORE_DETAILS = True
