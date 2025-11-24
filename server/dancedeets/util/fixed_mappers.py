import logging

from google.cloud import ndb
from google.cloud.ndb import exceptions as ndb_exceptions

from mapreduce import context
from mapreduce import handlers
from mapreduce import model
from mapreduce import util

#class FixedKeyRangeEntityIterator(datastore_range_iterators.KeyRangeEntityIterator):
#    def __iter__(self):
#        try:
#            return super(self, FixedKeyRangeEntityIterator).__iter__()
#        except ndb_exceptions.Timeout as e:
#            logging.warning("Got timeout while iterating: %s", e)
#            # Timeouts happen repeatedly on Managed VMs mapreduces, versus python27.
#            # However, if we've made forward progress, then a timeout is still
#            # a success that doesn't need retrying. So let's treat timeouts as
#            # a successful end-of-the-input-for-now response, so that we reschedule.


class FixedMapperWorkerCallbackHandler(handlers.MapperWorkerCallbackHandler):
    def _process_inputs(self, input_reader, shard_state, tstate, ctx):
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
                entity = next(iterator)
            except Exception as e:
                # Handle timeout-like exceptions
                if 'timeout' in str(e).lower():
                    logging.warning("Got timeout while iterating, going to finish and retry: %s", e)
                    finished_shard = False
                    break
                elif isinstance(e, StopIteration):
                    break
                else:
                    raise
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

            if isinstance(entity, ndb.Model):
                shard_state.last_work_item = repr(entity.key)
            else:
                shard_state.last_work_item = repr(entity)[:100]

            processing_limit -= 1

            if not self._process_datum(entity, input_reader, ctx, tstate):
                finished_shard = False
                break
            elif processing_limit == 0:
                finished_shard = False
                break

        # Flush context and its pools.
        self.slice_context.incr(context.COUNTER_MAPPER_WALLTIME_MS, int((self._time() - self._start_time) * 1000))

        return finished_shard

    def __return(self, shard_state, tstate, task_directive):
        # We need to remove the context, so other requests that run after us in this thread don't mistakenly see a context when they shouldn't.
        context.Context._set(None)
        return super(FixedMapperWorkerCallbackHandler, self).__return(shard_state, tstate, task_directive)

    def _drop_gracefully(self):
        """Drop worker task gracefully.

        Set current shard_state to failed. Controller logic will take care of
        other shards and the entire MR.
        """
        shard_id = self.request.headers[util._MR_SHARD_ID_TASK_HEADER]
        mr_id = self.request.headers[util._MR_ID_TASK_HEADER]
        shard_state = model.ShardState.get_by_shard_id(shard_id)
        mr_state = model.MapreduceState.get_by_job_id(mr_id)

        if shard_state and shard_state.active:
            logging.error('Would normally mark this shard for failure...and kill the entire mapreduce!')
            logging.error('But we ignore that and let this shard continue to run (and fail) instead.')
            # shard_state.set_for_failure()
            # config = util.create_datastore_write_config(mr_state.mapreduce_spec)
            # shard_state.put(config=config)
            raise Exception('Worker cannot run due to attempt to drop gracefully.')

    def _has_old_request_ended(self, shard_state):
        """
        The current _has_old_request_ended fails due to:
          File "/env/local/lib/python2.7/site-packages/mapreduce/handlers.py", line 240, in _try_acquire_lease
            if not self._has_old_request_ended(shard_state):
          File "/env/local/lib/python2.7/site-packages/mapreduce/handlers.py", line 305, in _has_old_request_ended
            logs = list(logservice.fetch(request_ids=request_ids))
          File "/env/local/lib/python2.7/site-packages/google/appengine/datastore/datastore_rpc.py", line 103, in positional_wrapper
            return wrapped(*args, **kwds)
          File "/env/local/lib/python2.7/site-packages/google/appengine/api/logservice/logservice.py", line 1103, in fetch
            '%s is not a valid request log id' % request_id)
          InvalidArgumentError:  is not a valid request log id

        So let's try to no-op it entirely, since it won't work for us anyway
        """
        return False
