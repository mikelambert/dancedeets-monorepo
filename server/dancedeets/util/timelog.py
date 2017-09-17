import logging
import time


def log_time_since(msg, time_start):
    diff = time.time() - time_start
    full_msg = 'Timing: Spent %s seconds: %s' % (msg, diff)
    if diff > 1.0:
        logging.error(full_msg)
    else:
        logging.info(full_msg)
