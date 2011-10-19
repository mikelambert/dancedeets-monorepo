from mapreduce import context
from mapreduce import control

import facebook
import fb_api

def start_map(batch_lookup, name, handler_spec, entity_kind):
        control.start_map(
                name=name,
                reader_spec='mapreduce.input_readers.DatastoreInputReader',
                handler_spec=handler_spec,
                shard_count=2, # since we want to stick it in the slow-queue, and don't care how fast it executes
                queue_name='slow-queue',
                mapper_parameters={
                        'entity_kind': entity_kind,
            'batch_lookup_fb_uid': batch_lookup.fb_uid,
                        'batch_lookup_fb_graph_access_token': batch_lookup.fb_graph.access_token,
                },
        )

def get_batch_lookup(allow_cache=True):
        ctx = context.get()
        params = ctx.mapreduce_spec.mapper.params
        fb_graph = facebook.GraphAPI(params['batch_lookup_fb_graph_access_token'])
        batch_lookup = fb_api.CommonBatchLookup(params['batch_lookup_fb_uid'], fb_graph, allow_cache=allow_cache)
    return batch_lookup
