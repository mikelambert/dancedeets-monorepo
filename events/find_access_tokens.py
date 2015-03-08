import logging

from mapreduce import base_handler
from mapreduce import context
from mapreduce import mapreduce_pipeline

import base_servlet
import fb_api
from . import eventdata
from . import event_updates

def test_user_on_events(user):
    logging.info("Trying user %s (expired %s)", user.fb_uid, user.expired_oauth_token)
    if user.expired_oauth_token:
        return
    ctx = context.get()
    params = ctx.mapreduce_spec.mapper.params
    event_ids = params['event_ids'].split(',')
    fbl = fb_api.FBLookup(user.fb_uid, user.fb_access_token)
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
    for db_event, fb_event in zip(found_db_events, found_fb_events):
        if not db_event.fb_event or db_event.fb_event['empty']:
            db_fb_events.append((db_event, fb_event))
    event_updates.update_and_save_event_batch(db_fb_events)

    # We can end the shard via this, though it's difficult to tell when *every* event_id has got a valid token.
    # ctx._shard_state.set_input_finished()

def save_valid_users_to_event(event_id, user_ids):
    db_event = eventdata.DBEvent.get_by_id(event_id)
    if not db_event:
        logging.error("Trying to load event %s to save user ids %s, but event did not exist", event_id, user_ids)
        return
    db_event.visible_to_fb_uids = user_ids
    db_event.put()
    yield '%s: %s' % (event_id, ','.join(user_ids))


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
            pipeline.start()
    post=get
