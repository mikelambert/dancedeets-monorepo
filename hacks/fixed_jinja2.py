import logging
import traceback

from jinja2 import environment


def fix_stacktraces():
    # Without ctypes available, jinja2 exceptions look worse.
    # This is a hack to print out some-good-information as best we can,
    # which is better than nothing when attempting to debug problems.
    real_handle_exception = environment.Environment.handle_exception

    def handle_exception(self, *args, **kwargs):
        logging.error('Template exception:\n%s', traceback.format_exc())
        real_handle_exception(self, *args, **kwargs)
    environment.Environment.handle_exception = handle_exception
