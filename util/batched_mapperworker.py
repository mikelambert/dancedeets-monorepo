from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from mapreduce import handlers

class BatchedMapperWorkerCallbackHandler(handlers.MapperWorkerCallbackHandler):
  def __init__(self, *args, **kwargs):
    super(BatchedMapperWorkerCallbackHandler, self).__init__(*args, **kwargs)
    self.all_data = []

  def process_data(self, data, input_reader, ctx, transient_shard_state):
    batch_size = ctx.mapreduce_spec.mapper.params.get("handle_batch_size", None)
    if not batch_size:
      return super(BatchedMapperWorkerCallbackHandler, self).process_data(data, input_reader, ctx, transient_shard_state)
    else:
      self.all_data.append(data)
      if len(self.all_data) >= batch_size:
        result = super(BatchedMapperWorkerCallbackHandler, self).process_data(self.all_data, input_reader, ctx, transient_shard_state)
        self.all_data = []
        return result
      return True

  def final_process_data(self, input_reader, ctx, transient_shard_state):
    batch_size = ctx.mapreduce_spec.mapper.params.get("handle_batch_size", None)
    if batch_size and self.all_data:
      super(BatchedMapperWorkerCallbackHandler, self).process_data(self.all_data, input_reader, ctx, transient_shard_state)
      self.all_data = []

