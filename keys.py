# For loading private keys
import yaml

__KEY_CONFIG = yaml.load(file('keys.yaml', 'r'))

def get(key):
    return __KEY_CONFIG[key]
