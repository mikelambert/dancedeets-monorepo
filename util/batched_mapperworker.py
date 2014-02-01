import logging

from mapreduce import context
from mapreduce import handlers
from mapreduce import input_readers

class BatchedMapperWorkerCallbackHandler(handlers.MapperWorkerCallbackHandler):
  def __init__(self, *args, **kwargs):
    super(BatchedMapperWorkerCallbackHandler, self).__init__(*args, **kwargs)
    self.all_data = []

  def _process_inputs(self,
                      input_reader,
                      shard_state,
                      tstate,
                      ctx):
    return super(BatchedMapperWorkerCallbackHandler, self)._process_inputs(input_reader, shard_state, tstate, ctx)

  def _process_datum(self, data, input_reader, ctx, transient_shard_state):
    if data is not input_readers.ALLOW_CHECKPOINT:
      batch_size = ctx.mapreduce_spec.mapper.params.get("handle_batch_size", None)
      if not batch_size:
        return super(BatchedMapperWorkerCallbackHandler, self)._process_datum(data, input_reader, ctx, transient_shard_state)
      else:
        self.all_data.append(data)
        if len(self.all_data) >= batch_size:
          for i in range(len(self.all_data) - 1): # subtract one, due to the increment() inside super._process_datum
            ctx.counters.increment(context.COUNTER_MAPPER_CALLS)
          result = super(BatchedMapperWorkerCallbackHandler, self)._process_datum(self.all_data, input_reader, ctx, transient_shard_state)
          self.all_data = []
          return result
        return True
    # potentially end early even if we didn't process data, just so we have time to process pending all_data
    if self._time() - self._start_time > handlers._SLICE_DURATION_SEC:
      if batch_size and self.all_data:
        result = super(BatchedMapperWorkerCallbackHandler, self)._process_datum(self.all_data, input_reader, ctx, transient_shard_state)
        self.all_data = []
      logging.debug("Spent %s seconds. Rescheduling",
                    self._time() - self._start_time)
      return False
    return True
