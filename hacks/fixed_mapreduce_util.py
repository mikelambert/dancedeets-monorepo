"""We monkey patch this function, so that mapreduce jobs are always run on the latest uploaded code version."""

import os
from mapreduce import util as mapreduce_util
from pipeline import pipeline as pipeline_pipeline
from pipeline import util as pipeline_util


def _get_task_host():
    return None

def patch_function():
    mapreduce_util._get_task_host = _get_task_host
    pipeline_util._get_task_target = _get_task_host
