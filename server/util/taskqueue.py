from google.appengine.api.taskqueue import *
from google.appengine.api import taskqueue


def add(*args, **kwargs):
    import logging
    import os
    from google.appengine.api import app_identity
    logging.info('TQADD: (*%s, **%s)', args, kwargs)
    logging.info('TQADD: DEFAULT_VERSION_HOSTNAME = %s', os.getenv('DEFAULT_VERSION_HOSTNAME'))
    logging.info('TQADD: app_identity.get_default_version_hostname = %s', app_identity.get_default_version_hostname())
    logging.info('TQADD: SERVER_SOFTWARE = %s', os.environ.get('SERVER_SOFTWARE', ''))
    kwargs['target'] = taskqueue.DEFAULT_APP_VERSION
    result = taskqueue.add(*args, **kwargs)
    logging.info('TQADD: self.__target = %s', result._Task__target)
    logging.info('TQADD: self.__headers = %s', result._Task__headers)
    return result
