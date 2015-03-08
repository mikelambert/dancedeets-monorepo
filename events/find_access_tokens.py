import logging

from mapreduce import base_handler
from mapreduce import context
from mapreduce import mapreduce_pipeline

import base_servlet
import fb_api
from events import eventdata

def test_user_on_events(user):
    if user.expired_oauth_token:
        return
    ctx = context.get()
    params = ctx.mapreduce_spec.mapper.params
    event_ids = params['event_ids'].split(',')
    fbl = fb_api.FBLookup(user.fb_uid, user.fb_access_token)
    try:
        fb_events = fbl.get_multi(fb_api.LookupEvent, event_ids)
    except fb_api.ExpiredOAuthToken:
        # Not longer a valid source for access_tokens
        return
    for fb_event, event_id in zip(fb_events, event_ids):
        if fb_event and not fb_event['empty']:
            yield (event_id, user.fb_uid)

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
            'events.event_reloading_tasks.test_user_on_events',
            'events.event_reloading_tasks.save_valid_users_to_event',
            'mapreduce.input_readers.DatastoreInputReader',
            'mapreduce.output_writers.GoogleCloudStorageOutputWriter',
            mapper_params={
                'entity_kind': 'users.users.User',
                'filters': filters,
                'event_ids': ','.join(event_ids),
            },
            reducer_params={
                'output_writer': {
                    'bucket_name': 'dancedeets-hrd',
                    'content_type': 'text/plain',
                }
            },
            shards=1
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
