# For loading private keys
import logging
import os
import yaml


def _get_config(filename):
    _filename = os.path.join(os.path.dirname(__file__), '..', filename)
    if os.path.exists(_filename):
        with open(_filename, 'r') as f:
            return yaml.safe_load(f)
    else:
        logging.error('Cannot find %s, using an empty keys file instead.', filename)
        return {}


__KEY_CONFIG = _get_config('keys.yaml')
__DEV_KEY_CONFIG = _get_config('keys-dev.yaml')

NO_KEY = 'NO_KEY'


def get(key):
    """Get a key from config files or environment variables.

    Priority order:
    1. keys.yaml
    2. keys-dev.yaml
    3. Environment variable (uppercase with underscores, e.g. google_server_key -> GOOGLE_SERVER_KEY)
    4. NO_KEY fallback
    """
    # First check config files
    value = __KEY_CONFIG.get(key, __DEV_KEY_CONFIG.get(key))
    if value:
        return value

    # Then check environment variable (convert to uppercase with underscores)
    env_key = key.upper()
    env_value = os.environ.get(env_key)
    if env_value:
        return env_value

    return NO_KEY
