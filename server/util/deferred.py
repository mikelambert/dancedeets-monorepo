from google.appengine.ext.deferred import *
from google.appengine.ext import deferred


def defer(*args, **kwargs):
    # Since defer() itself adds in a target header regardlesss,
    # we cannot pass in a hostname here at all.
    kwargs['_target'] = taskqueue.DEFAULT_APP_VERSION
    return deferred.defer(*args, **kwargs)
