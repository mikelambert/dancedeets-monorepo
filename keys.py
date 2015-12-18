# For loading private keys
import logging
import os
import yaml

_filename = os.path.join(os.path.dirname(__file__), 'keys.yaml')
if os.path.exists(_filename):
    __KEY_CONFIG = yaml.load(file(_filename, 'r'))
else:
    logging.error('Cannot find keys.yaml, using an empty keys file instead.')
    __KEY_CONFIG = {}

def get(key):
    return __KEY_CONFIG[key]
