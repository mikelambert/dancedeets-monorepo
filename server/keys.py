# For loading private keys
import logging
import os
import yaml


def _get_config(filename):
    _filename = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(_filename):
        return yaml.load(file(_filename, 'r'))
    else:
        logging.error('Cannot find keys.yaml, using an empty keys file instead.')
        return {}


__KEY_CONFIG = _get_config('keys.yaml')
__DEV_KEY_CONFIG = _get_config('keys-dev.yaml')

NO_KEY = 'NO_KEY'


def get(key):
    return __KEY_CONFIG.get(key, __DEV_KEY_CONFIG.get(key, NO_KEY))
