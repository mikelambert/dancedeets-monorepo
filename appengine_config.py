def tasklets_toplevel(func):
    """A sync tasklet that sets a fresh default Context.

    Use this for toplevel view functions such as
    webapp.RequestHandler.get() or Django view functions.
    """
    from google.appengine.ext.ndb import tasklets
    synctaskletfunc = tasklets.synctasklet(func)    # wrap at declaration time.
    @tasklets.utils.wrapping(func)
    def add_context_wrapper(*args, **kwds):
        tasklets._state.clear_all_pending()
        # Create and install a new context.
        ctx = tasklets.make_default_context()
        try:
            tasklets.set_context(ctx)
            return synctaskletfunc(*args, **kwds)
        finally:
            tasklets.set_context(None)
            tasklets._state.clear_all_pending()
    return add_context_wrapper


def webapp_add_wsgi_middleware(app):
    #from google.appengine.ext.ndb import tasklets
    app = tasklets_toplevel(app)

    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)

    return app

# We don't need such real-time statistics (normally 1 second) on the mapreduce job.
# More of an optimization to save on the associated database Get/Put every second.
mapreduce__CONTROLLER_PERIOD_SEC = 5

appstats_MAX_STACK = 25
appstats_MAX_REPR = 100
appstats_MAX_LOCALS = 5

appstats_RECORD_FRACTION = 1.0

appstats_DATASTORE_DETAILS = True
