import logging

def tasklets_toplevel(func):
    """A sync tasklet that sets a fresh default Context.

    Use this for toplevel view functions such as
    webapp.RequestHandler.get() or Django view functions.
    """
    from google.appengine.ext.ndb import tasklets
    from google.appengine.ext.ndb import eventloop
    @tasklets.utils.wrapping(func)
    def add_context_wrapper(*args, **kwds):
        tasklets._state.clear_all_pending()
        ctx = tasklets.make_default_context()
        try:
            tasklets.set_context(ctx)
            result = func(*args, **kwds)
            # We may be surrounding a generator (like the appstats middleware)
            # So let's be sure we properly re-yield, so that the finally clause
            # runs correctly at the end of the yields, and not when we return a
            # generator ourselves (which then leaves it un-cleaned-up at the end).
            if result is not None:
                for value in result:
                    yield value
        finally:
            # Clean up everything we can. Emptying the context and pending Futures is the most important.
            tasklets.set_context(None)
            tasklets._state.clear_all_pending()
            # But we clean out the event_loop early for good measure,
            # since it would happen on the next request to this thread anyway.
            if eventloop._state.event_loop:
                eventloop._state.event_loop.clear()
                eventloop._state.event_loop = None
    return add_context_wrapper


def webapp_add_wsgi_middleware(app):
    #from google.appengine.ext.ndb import tasklets
    from google.appengine.ext.appstats import recording

    app = recording.appstats_wsgi_middleware(app)

    app = tasklets_toplevel(app)

    # Should only use this in cases of serialized execution of requests in a multi-threaded processes.
    # So setdeploy manually, and test from there. Never a live server, as it would be both broken *and* slow.
    # import memory_leaks
    #app = memory_leaks.leak_middleware(app)

    return app

NDB_LOGGING_LEVEL = 0
if NDB_LOGGING_LEVEL > 0:
    from google.appengine.ext.ndb import utils
    utils.logging_debug = logging.info
    from google.appengine.ext.ndb import eventloop
    eventloop._logging_debug = logging.info
    if NDB_LOGGING_LEVEL > 1:
        from google.appengine.ext.ndb import tasklets
        tasklets._logging_debug = logging.info

# This was a failed attempt at trying to keep a deque-style FIFO ordering to the event_loop.rpcs
RPC_ORDERING = False
if RPC_ORDERING:
    import collections
    from google.appengine.ext.ndb import eventloop
    orig_get_event_loop = eventloop.get_event_loop
    def new_get_event_loop():
        event_loop = orig_get_event_loop()
        event_loop.rpcs = collections.OrderedDict()
        return event_loop
    #eventloop.get_event_loop = new_get_event_loop


# We don't need such real-time statistics (normally 1 second) on the mapreduce job.
# More of an optimization to save on the associated database Get/Put every second.
mapreduce__CONTROLLER_PERIOD_SEC = 5

appstats_MAX_STACK = 25
appstats_MAX_REPR = 100
appstats_MAX_LOCALS = 5

appstats_RECORD_FRACTION = 1.0

appstats_DATASTORE_DETAILS = True
