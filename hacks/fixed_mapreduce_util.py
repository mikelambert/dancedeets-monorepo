"""We monkey patch this function, so that mapreduce jobs are always run on the latest uploaded code version."""

import os
from mapreduce import util

def _get_task_host():
  """Get the Host header value for all mr tasks.

  Task Host header determines which instance this task would be routed to.

  Current module id is just the module's name. It could be "default"
  Default version hostname is app_id.appspot.com

  Returns:
    A complete host name is of format module.app_id.appspot.com
  If module is the default module, just app_id.appspot.com.
  If "default" version doesn't exist, the url is routed to the
  default version.
  """
  default_host = os.environ["DEFAULT_VERSION_HOSTNAME"]
  module = os.environ["CURRENT_MODULE_ID"]
  if os.environ["CURRENT_MODULE_ID"] == "default":
    return "%s" % (default_host)
  return "%s.%s" % (module, default_host)

def patch_function():
  util._get_task_host = _get_task_host
