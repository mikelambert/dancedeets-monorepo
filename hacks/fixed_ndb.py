import collections
import logging

from google.appengine.ext.ndb import eventloop
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import apiproxy_rpc

def tasklets_toplevel(func):
    """A sync tasklet that sets a fresh default Context.

    Use this for toplevel view functions such as
    webapp.RequestHandler.get() or Django view functions.
    """
    from google.appengine.ext.ndb import tasklets
    from google.appengine.ext.ndb import eventloop
    @tasklets.utils.wrapping(func)
    def add_context_wrapper(*args, **kwds):
        tasklets._state.clear_all_pending()
        ctx = tasklets.make_default_context()
        try:
            tasklets.set_context(ctx)
            result = func(*args, **kwds)
            # We may be surrounding a generator (like the appstats middleware)
            # So let's be sure we properly re-yield, so that the finally clause
            # runs correctly at the end of the yields, and not when we return a
            # generator ourselves (which then leaves it un-cleaned-up at the end).
            if result is not None:
                for value in result:
                    yield value
        finally:
            # Clean up everything we can. Emptying the context and pending Futures is the most important.
            tasklets.set_context(None)
            tasklets._state.clear_all_pending()
            # But we clean out the event_loop early for good measure,
            # since it would happen on the next request to this thread anyway.
            if eventloop._state.event_loop:
                eventloop._state.event_loop.clear()
                eventloop._state.event_loop = None
    return add_context_wrapper


def patch_logging(logging_level):
    if logging_level > 0:
        from google.appengine.ext.ndb import utils
        utils.logging_debug = logging.info
        from google.appengine.ext.ndb import eventloop
        eventloop._logging_debug = logging.info
        if logging_level > 1:
            from google.appengine.ext.ndb import tasklets
            tasklets._logging_debug = logging.info


class OrderedEventLoop(eventloop.EventLoop):
  def __init__(self):
    super(OrderedEventLoop, self).__init__()
    self.rpcs = collections.OrderedDict()


@classmethod
def __check_one(cls, rpcs):
  rpc = None
  logging.info('Pending RPCs: %s', rpcs)
  for rpc in rpcs:
    assert isinstance(rpc, cls), repr(rpc)
    # Original:
    # state = rpc.__rpc.state
    # Revised:
    state = rpc.state
    if state == apiproxy_rpc.RPC.FINISHING:
      # Original:
      # rpc.__call_user_callback()
      # Revised:
      rpc.wait()
      logging.info('Found finished RPC: %s', rpc)
      return rpc, None
    assert state != apiproxy_rpc.RPC.IDLE, repr(rpc)
  logging.info('No finished RPCs, going to wait for first RPC: %s', rpcs[0])
  # This is the important changed line in this whole function:
  # We want to return the oldest RPC to execute, not a random one.
  return None, rpcs[0]


def fix_rpc_ordering():
    # This attempts to force a FIFO ordering on RPC execution in the eventloop (as opposed to random RPC execution)
    eventloop.EventLoop = OrderedEventLoop
    assert hasattr(apiproxy_stub_map.UserRPC, '_UserRPC__check_one')
    apiproxy_stub_map.UserRPC._UserRPC__check_one = __check_one
