"""NDB compatibility shim for Cloud NDB migration.

This module previously contained hacks for App Engine NDB.
Cloud NDB handles context management differently, so most of these
functions are now no-ops.

The NDB context is now managed by the NDBContextMiddleware in main.py.
"""

import logging


def tasklets_toplevel(func):
    """No-op decorator for Cloud NDB compatibility.

    Previously this managed NDB context, but Cloud NDB uses
    NDBContextMiddleware instead.
    """
    # In Cloud NDB, context is managed by the middleware
    # This is now a pass-through
    return func


def patch_logging(logging_level):
    """No-op for Cloud NDB compatibility.

    Cloud NDB has different logging configuration.
    """
    if logging_level > 0:
        logging.info('NDB logging patches not applicable to Cloud NDB')


def fix_rpc_ordering():
    """No-op for Cloud NDB compatibility.

    Cloud NDB uses different RPC mechanisms.
    """
    pass
