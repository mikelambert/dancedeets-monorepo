from google.appengine.ext.deferred import *
from google.appengine.ext import deferred

def defer(*args, **kwargs):
    kwargs['_target'] = taskqueue.DEFAULT_APP_VERSION
    return deferred.defer(*args, **kwargs)
