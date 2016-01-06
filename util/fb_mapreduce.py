import datetime
import random

from google.appengine.ext import ndb

from mapreduce import context
from mapreduce import control
from mapreduce import util

import fb_api
from users import users

def start_map(
    fbl,
    name,
    handler_spec,
    entity_kind,
    filters=None,
    handle_batch_size=None,
    output_writer_spec=None,
    output_writer=None,
    queue='slow-queue',
    extra_mapper_params=None,
    randomize_tokens=True,
):
    filters = filters or []
    output_writer = output_writer or {}
    extra_mapper_params = extra_mapper_params or {}
    mapper_params = {
        'entity_kind': entity_kind,
        'handle_batch_size': handle_batch_size,
        'filters': filters,
        'output_writer': output_writer,
    }
    mapper_params.update(_get_fblookup_params(fbl, randomize_tokens=randomize_tokens))
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

def get_fblookup(user=None):
    ctx = context.get()
    params = ctx.mapreduce_spec.mapper.params
    if params.get('fbl_access_tokens'):
        parent_token = random.choice(params.get('fbl_access_tokens'))
    else:
        parent_token = params['fbl_access_token']
    access_token = (user and user.fb_access_token or parent_token)
    fbl = fb_api.FBLookup(
        user and user.fb_uid or params['fbl_fb_uid'],
        access_token)
    fbl.allow_cache = params['fbl_allow_cache']
    fbl.force_updated = params['fbl_force_updated']
    if params.get('fbl_oldest_allowed') is not None:
        fbl.db.oldest_allowed = params['fbl_oldest_allowed']
    return fbl

def _get_fblookup_params(fbl, randomize_tokens=False):
    params = {
        'fbl_fb_uid': fbl.fb_uid,
        'fbl_allow_cache': fbl.allow_cache,
        'fbl_force_updated': fbl.force_updated,
    }
    if fbl.db.oldest_allowed != datetime.datetime.min:
        params['fbl_oldest_allowed'] = fbl.db.oldest_allowed
    if randomize_tokens:
        params['fbl_access_tokens'] = _get_multiple_tokens(token_count=20)
    else:
        params['fbl_access_token'] = fbl.access_token
    return params

def _get_multiple_tokens(token_count):
    good_users = users.User.query(users.User.key>=ndb.Key(users.User, '701004'), users.User.expired_oauth_token==False).fetch(token_count)
    tokens = [x.fb_access_token for x in good_users]
    return tokens

def mr_wrap(func):
    if util.is_generator(func):
        def map_func(*args, **kwargs):
            fbl = get_fblookup()
            # this passes the generator on to the client as a generator, while still having this function be detected as a generator (instead of just returning the generator directly, which would work but not let this function be detected as a generator)
            for x in func(fbl, *args, **kwargs):
                yield x
    else:
        def map_func(*args, **kwargs):
            fbl = get_fblookup()
            return func(fbl, *args, **kwargs)
    return map_func

def mr_user_wrap(func):
    def map_func(user, *args, **kwargs):
        fbl = get_fblookup(user=user)
        return func(fbl, user, *args, **kwargs)
    return map_func

def nomr_wrap(func):
    def map_func(*args, **kwargs):
        return func(*args, **kwargs)
    return map_func
