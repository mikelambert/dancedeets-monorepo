import logging

import cloudstorage

from mapreduce import base_handler
from mapreduce import context
from mapreduce import mapper_pipeline
from mapreduce import mapreduce_pipeline
from mapreduce import pipeline_base
from mapreduce import util

import app
import base_servlet
import fb_api
from . import eventdata
from . import event_updates
from util import fb_mapreduce

def test_user_on_events(user):
    logging.info("Trying user %s (expired %s)", user.fb_uid, user.expired_oauth_token)
    if user.expired_oauth_token:
        return
    # TODO: Relies on us keeping these up to date!
    if not user.num_auto_added_events and not user.num_hand_added_events:
        return
    ctx = context.get()
    params = ctx.mapreduce_spec.mapper.params
    event_ids = params['event_ids'].split(',')
    fbl = user.get_fblookup()
    fbl.allow_cache = False
    try:
        fb_events = fbl.get_multi(fb_api.LookupEvent, event_ids)
    except fb_api.ExpiredOAuthToken:
        # Not longer a valid source for access_tokens
        return
    found_fb_events = [x for x in fb_events if x and not x['empty']]
    for fb_event in found_fb_events:
        yield (fb_event['info']['id'], user.fb_uid)

    # Found some good stuff, let's save and update the db events
    found_db_events = eventdata.DBEvent.get_by_ids([x['info']['id'] for x in found_fb_events])
    db_fb_events = []
    for db_event, new_fb_event in zip(found_db_events, found_fb_events):
        if db_event.has_content():
            db_fb_events.append((db_event, new_fb_event))
    event_updates.update_and_save_events(db_fb_events)

    # We can end the shard via this, though it's difficult to tell when *every* event_id has got a valid token.
    # ctx._shard_state.set_input_finished()

def save_valid_users_to_event(event_id, user_ids):
    db_event = eventdata.DBEvent.get_by_id(event_id)
    if not db_event:
        logging.error("Trying to load event %s to save user ids %s, but event did not exist", event_id, user_ids)
        return
    db_event.visible_to_fb_uids = user_ids
    db_event.put()
    yield '%s: %s\n' % (event_id, ','.join(user_ids))


class FindAccessTokensForEventsPipeline(base_handler.PipelineBase):

    def run(self, event_ids):
        # Can't do != comparators in our appengine mapreduce queries
        # filters = [('expired_oauth_token', '!=', True)]
        # Unfortunately, many users have a value equal to None, so can't filter on this
        # filters = [('expired_oauth_token', '=', False)]
        # So for now, let's just process all of them, and skip them inside test_user_on_events
        filters = []
        # output = yield ...
        yield mapreduce_pipeline.MapreducePipeline(
            'Find valid access_tokens for events',
            'events.find_access_tokens.test_user_on_events',
            'events.find_access_tokens.save_valid_users_to_event',
            'mapreduce.input_readers.DatastoreInputReader',
            'mapreduce.output_writers.GoogleCloudStorageOutputWriter',
            mapper_params={
                'entity_kind': 'users.users.User',
                'filters': filters,
                'event_ids': ','.join(event_ids),
            },
            reducer_params={
                'output_writer': {
                    'bucket_name': 'dancedeets-hrd.appspot.com',
                    'content_type': 'text/plain',
                }
            },
            shards=2,
        )

class FindAccessTokensForEventsHandler(base_servlet.BaseTaskRequestHandler):
    def get(self):
        event_ids = [x for x in self.request.get('event_ids').split(',') if x]
        real_event_ids = [x.string_id() for x in eventdata.DBEvent.get_by_ids(event_ids, keys_only=True) if x]
        logging.info("Passed IDs %s, going to run mapreduce search with IDs %s", event_ids, real_event_ids)
        if event_ids:
            pipeline = FindAccessTokensForEventsPipeline(real_event_ids)
            pipeline.start(queue_name='slow-queue')
    post=get

def map_events_needing_access_tokens(all_db_events):
    fbl = fb_mapreduce.get_fblookup()
    db_events = [x for x in all_db_events if not x.visible_to_fb_uids]
    try:
        fb_events = fbl.get_multi(fb_api.LookupEvent, [x.fb_event_id for x in db_events])
    except fb_api.ExpiredOAuthToken:
        # Not longer a valid source for access_tokens
        logging.exception("ExpiredOAuthToken")
    for db_event, fb_event in zip(db_events, fb_events):
        if fb_event['empty'] == fb_api.EMPTY_CAUSE_INSUFFICIENT_PERMISSIONS:
            yield '%s\n' % db_event.fb_event_id

def file_identity(x):
    result = x.read()
    yield result

class CombinerPipeline(pipeline_base._OutputSlotsMixin,
                       pipeline_base.PipelineBase):
  output_names = mapper_pipeline.MapperPipeline.output_names

  def run(self,
          job_name,
          bucket_name,
          filenames):
    filenames_only = (
        util.strip_prefix_from_items("/%s/" % bucket_name, filenames))
    params = {
        "output_writer": {
            "bucket_name": bucket_name,
            "content_type": "text/plain",
        },
        "input_reader": {
            "bucket_name": bucket_name,
            "objects": filenames_only,
        }
    }
    yield mapper_pipeline.MapperPipeline(
        job_name + "-combine",
        'events.find_access_tokens.file_identity',
        'mapreduce.input_readers.GoogleCloudStorageInputReader',
        'mapreduce.output_writers.GoogleCloudStorageOutputWriter',
        params,
        shards=1)


class PassFileToAccessTokenFinder(pipeline_base._OutputSlotsMixin,
                     pipeline_base.PipelineBase):
  output_names = mapper_pipeline.MapperPipeline.output_names

  def run(self, filenames):
    handle = cloudstorage.open(filenames[0])
    event_ids = handle.read().split('\n')
    handle.close()
    yield FindAccessTokensForEventsPipeline(event_ids)

class FindEventsNeedingAccessTokensPipeline(base_handler.PipelineBase):
    def run(self, fbl_json, filters):
        bucket_name = 'dancedeets-hrd.appspot.com'
        params = {
            'entity_kind': 'events.eventdata.DBEvent',
            'filters': filters,
            'handle_batch_size': 20,
            'output_writer': {
                'bucket_name': bucket_name,
                'content_type': 'text/plain',
            }
        }
        params.update(fbl_json)
        # This should use cache, so we can go faster
        find_events_needing_access_tokens = (
            yield mapper_pipeline.MapperPipeline(
                'Find valid events needing access_tokens',
                'events.find_access_tokens.map_events_needing_access_tokens',
                'mapreduce.input_readers.DatastoreInputReader',
                'mapreduce.output_writers.GoogleCloudStorageOutputWriter',
                params=params,
                shards=10,
            ))
        # This will be a single shard
        single_file_of_fb_events = yield CombinerPipeline(
            "Combine event lists into single file",
            bucket_name,
            find_events_needing_access_tokens)
        # This will use more shards
        yield PassFileToAccessTokenFinder(
            single_file_of_fb_events)


@app.route('/tasks/find_events_needing_access_tokens')
class FindEventsNeedingAccessTokensHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        time_period = self.request.get('time_period')
        # TODO: WEB_EVENTS
        filters = [('namespace', '=', eventdata.Namespace.FACEBOOK)]
        if time_period:
            filters.append(('search_time_period', '=', time_period))
        pipeline = FindEventsNeedingAccessTokensPipeline(fb_mapreduce.get_fblookup_params(self.fbl), filters)
        pipeline.start(queue_name='slow-queue')
    post=get
