import logging
from mapreduce import context
from mapreduce import control

import facebook
import fb_api

def start_map(batch_lookup, name, handler_spec, entity_kind, reader_spec='mapreduce.input_readers.DatastoreInputReader'):
        control.start_map(
                name=name,
                reader_spec=reader_spec,
                handler_spec=handler_spec,
                shard_count=2, # since we want to stick it in the slow-queue, and don't care how fast it executes
                queue_name='slow-queue',
                mapper_parameters={
                        'entity_kind': entity_kind,
            'batch_lookup_fb_uid': batch_lookup.fb_uid,
                        'batch_lookup_fb_graph_access_token': batch_lookup.fb_graph.access_token,
            'batch_lookup_allow_cache': batch_lookup.allow_cache,
                },
        )

def get_batch_lookup(user=None):
        ctx = context.get()
        params = ctx.mapreduce_spec.mapper.params
        fb_graph = facebook.GraphAPI(user and user.fb_access_token or params['batch_lookup_fb_graph_access_token'])
        batch_lookup = fb_api.CommonBatchLookup(user and user.fb_uid or params['batch_lookup_fb_uid'], fb_graph, allow_cache=params['batch_lookup_allow_cache'])
    return batch_lookup


def mr_wrap(func):
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
