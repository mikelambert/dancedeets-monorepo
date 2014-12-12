import logging

from google.appengine.api import datastore_errors
from google.appengine.ext import db
from google.appengine.ext import ndb

from mapreduce import context
from mapreduce import handlers

#class FixedKeyRangeEntityIterator(datastore_range_iterators.KeyRangeEntityIterator):
#    def __iter__(self):
#        try:
#            return super(self, FixedKeyRangeEntityIterator).__iter__()
#        except datastore_errors.Timeout as e:
#            logging.warning("Got timeout while iterating: %s", e)
#            # Timeouts happen repeatedly on Managed VMs mapreduces, versus python27.
#            # However, if we've made forward progress, then a timeout is still
#            # a success that doesn't need retrying. So let's treat timeouts as
#            # a successful end-of-the-input-for-now response, so that we reschedule.

class FixedMapperWorkerCallbackHandler(handlers.MapperWorkerCallbackHandler):

  def _process_inputs(self,
                      input_reader,
                      shard_state,
                      tstate,
                      ctx):
    """Read inputs, process them, and write out outputs.

    This is the core logic of MapReduce. It reads inputs from input reader,
    invokes user specified mapper function, and writes output with
    output writer. It also updates shard_state accordingly.
    e.g. if shard processing is done, set shard_state.active to False.

    If errors.FailJobError is caught, it will fail this MR job.
    All other exceptions will be logged and raised to taskqueue for retry
    until the number of retries exceeds a limit.

    Args:
      input_reader: input reader.
      shard_state: shard state.
      tstate: transient shard state.
      ctx: mapreduce context.

    Returns:
      Whether this shard has finished processing all its input split.
    """
    processing_limit = self._processing_limit(tstate.mapreduce_spec)
    if processing_limit == 0:
      return

    finished_shard = True
    # Input reader may not be an iterator. It is only a container.
    iterator = iter(input_reader)

    while True:
      try:
        entity = iterator.next()
      except datastore_errors.Timeout as e:
        logging.warning("Got timeout while iterating, going to finish and retry: %s", e)
        finished_shard = False
        break
      except StopIteration:
        break
      # Reading input got exception. If we assume
      # 1. The input reader have done enough retries.
      # 2. The input reader can still serialize correctly after this exception.
      # 3. The input reader, upon resume, will try to re-read this failed
      #    record.
      # 4. This exception doesn't imply the input reader is permanently stuck.
      # we can serialize current slice immediately to avoid duplicated
      # outputs.
      # TODO(user): Validate these assumptions on all readers. MR should
      # also have a way to detect fake forward progress.

      if isinstance(entity, db.Model):
        shard_state.last_work_item = repr(entity.key())
      elif isinstance(entity, ndb.Model):
        shard_state.last_work_item = repr(entity.key)
      else:
        shard_state.last_work_item = repr(entity)[:100]

      processing_limit -= 1

      if not self._process_datum(
          entity, input_reader, ctx, tstate):
        finished_shard = False
        break
      elif processing_limit == 0:
        finished_shard = False
        break

    # Flush context and its pools.
    self.slice_context.incr(
        context.COUNTER_MAPPER_WALLTIME_MS,
        int((self._time() - self._start_time)*1000))

    return finished_shard
