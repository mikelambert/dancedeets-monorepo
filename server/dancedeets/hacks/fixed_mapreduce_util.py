"""We monkey patch this function, so that mapreduce jobs are always run on the latest uploaded code version."""

import os
from mapreduce import model
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

    # This is intended to protect against two tasks running concurrently
    # Can happen from messing around in the cloud task admin page,
    # or just general randomness of the task execution system,
    # as it requires idempotency (presumably) for this reason.
    original_copy_from = model.ShardState.copy_from

    def copy_from(self, other_state):
        # If the other_state slice_id is old,
        # we don't want to copy over the relevant values.
        # So instead, only copy things over if its not older,
        # or if the result_status/active/input_finished changed.
        if (
            other_state.slice_id >= self.slice_id or (
                other_state.active != self.active or other_state.result_status != self.result_stats or
                other_state.input_finished != self.input_finished
            )
        ):
            original_copy_from(self, other_state)

    model.ShardState.copy_from = copy_from
