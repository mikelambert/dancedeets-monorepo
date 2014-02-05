from mapreduce import context
from mapreduce import control
from mapreduce import util

import facebook
import fb_api

def start_map(batch_lookup, name, handler_spec, entity_kind, filters=None, handle_batch_size=None, output_writer_spec=None, extra_mapper_params=None, queue='slow-queue'):
    filters = filters or []
    extra_mapper_params = extra_mapper_params or {}
    mapper_params = {
        'entity_kind': entity_kind,
        'handle_batch_size': handle_batch_size,
        'batch_lookup_fb_uid': batch_lookup.fb_uid,
        'batch_lookup_fb_graph_access_token': batch_lookup.fb_graph.access_token,
        'batch_lookup_allow_cache': batch_lookup.allow_cache,
        'filters': filters,
    }
    mapper_params.update(extra_mapper_params)
    control.start_map(
        name=name,
        reader_spec='mapreduce.input_readers.DatastoreInputReader',
        handler_spec=handler_spec,
        output_writer_spec=output_writer_spec,
        shard_count=8, # since we want to stick it in the slow-queue, and don't care how fast it executes
        queue_name=queue,
        mapper_parameters=mapper_params,
    )

def get_batch_lookup(user=None):
    ctx = context.get()
    params = ctx.mapreduce_spec.mapper.params
    fb_graph = facebook.GraphAPI(user and user.fb_access_token or params['batch_lookup_fb_graph_access_token'])
    batch_lookup = fb_api.CommonBatchLookup(user and user.fb_uid or params['batch_lookup_fb_uid'], fb_graph, allow_cache=params['batch_lookup_allow_cache'])
    return batch_lookup


def mr_wrap(func):
    if util.is_generator(func):
        def map_func(*args, **kwargs):
            batch_lookup = get_batch_lookup()
            # this passes the generator on to the client as a generator, while still having this function be detected as a generator (instead of just returning the generator directly, which would work but not let this function be detected as a generator)
            for x in func(batch_lookup, *args, **kwargs):
                yield x
    else:
        def map_func(*args, **kwargs):
            batch_lookup = get_batch_lookup()
            return func(batch_lookup, *args, **kwargs)
    return map_func

def mr_user_wrap(func):
    def map_func(user, *args, **kwargs):
        batch_lookup = get_batch_lookup(user=user)
        return func(batch_lookup, user, *args, **kwargs)
    return map_func

def nomr_wrap(func):
    def map_func(*args, **kwargs):
        return func(*args, **kwargs)
    return map_func
