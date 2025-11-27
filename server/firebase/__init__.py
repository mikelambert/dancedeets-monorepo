"""
Compatibility stub for python-firebase package.
The original python-firebase package is not Python 3.11 compatible (uses 'async' as module name).
This stub provides minimal API compatibility for battle_brackets.signup_servlets.
"""

import logging

logger = logging.getLogger(__name__)


class FirebaseAuthentication:
    """Stub for FirebaseAuthentication"""

    def __init__(self, secret, email=None):
        self.secret = secret
        self.email = email
        logger.warning("FirebaseAuthentication stub: Firebase authentication is disabled")


class FirebaseApplication:
    """Stub for FirebaseApplication"""

    def __init__(self, dsn, authentication=None):
        self.dsn = dsn
        self.authentication = authentication
        logger.warning(f"FirebaseApplication stub: Firebase Realtime Database access is disabled for {dsn}")

    def get(self, path, name=None):
        """Stub for Firebase get operation"""
        logger.warning(f"FirebaseApplication.get stub: Would fetch {path}/{name}")
        return {}

    def put(self, path, name, data):
        """Stub for Firebase put operation"""
        logger.warning(f"FirebaseApplication.put stub: Would write to {path}/{name}")
        return data

    def delete(self, path, name):
        """Stub for Firebase delete operation"""
        logger.warning(f"FirebaseApplication.delete stub: Would delete {path}/{name}")
        return True


# For backward compatibility
firebase = type('firebase', (), {
    'FirebaseAuthentication': FirebaseAuthentication,
    'FirebaseApplication': FirebaseApplication,
})()
