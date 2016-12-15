from google.appengine.api.taskqueue import *
from google.appengine.api import taskqueue

def add(*args, **kwargs):
    kwargs['target'] = taskqueue.DEFAULT_APP_VERSION
    return taskqueue.add(*args, **kwargs)
