# For loading private keys
import os
import yaml

__KEY_CONFIG = yaml.load(file(os.path.join(os.path.dirname(__file__), 'keys.yaml'), 'r'))

def get(key):
    return __KEY_CONFIG[key]
