"""We monkey patch this function, so that mapreduce jobs are always run on the latest uploaded code version."""

import os
from mapreduce import util as mapreduce_util
from pipeline import util as pipeline_util


def _get_task_host():
    default_host = os.environ["DEFAULT_VERSION_HOSTNAME"]
    module = os.environ["CURRENT_MODULE_ID"]
    if os.environ["CURRENT_MODULE_ID"] == "default":
        return "%s" % (default_host)
    return "%s.%s" % (module, default_host)


def _get_task_target():
    module = os.environ["CURRENT_MODULE_ID"]
    return module


def patch_function():
    mapreduce_util._get_task_host = _get_task_host
    pipeline_util._get_task_target = _get_task_target
