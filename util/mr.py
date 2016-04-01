import json
from mapreduce import context


def increment(key, delta=1):
    ctx = context.get()
    if ctx:
        ctx.counters.increment(key, delta=delta)


def process_mr_params(params):
    if 'filters' in params:
        params['filters'] = json.loads(params['filters'])
