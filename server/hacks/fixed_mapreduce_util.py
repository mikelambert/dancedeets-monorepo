"""We monkey patch this function, so that mapreduce jobs are always run on the latest uploaded code version."""

import os
from mapreduce import parameters
from mapreduce import util as mapreduce_util
from pipeline import util as pipeline_util


def _get_task_host():
    default_host = os.environ["DEFAULT_VERSION_HOSTNAME"]
    module = _get_task_target()
    if module == "default":
        return "%s" % (default_host)
    return "%s.%s" % (module, default_host)


def _get_task_target():
    module = os.environ["CURRENT_MODULE_ID"]
    module = 'batch'
    return module


def patch_function():
    mapreduce_util._get_task_host = _get_task_host
    pipeline_util._get_task_target = _get_task_target

    # This is the max-timeout we wait before giving up.
    # Normally it'd check the logs-API to verify, but we run on managed VMs where that doesn't exist
    # Without this, it'd wait 10.5 minutes to restart the mapreduce, but we should do much better...
    parameters._MAX_LEASE_DURATION_SEC = parameters.config._SLICE_DURATION_SEC * 1.2
