import json


def process_mr_params(params):
    if 'filters' in params:
        params['filters'] = json.loads(params['filters'])
