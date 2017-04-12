from mapreduce import control

import app
import base_servlet
from rankings import cities
from util import dates
from . import pubsub

@app.route('/tasks/social_publisher')
class SocialPublisherHandler(base_servlet.BaseTaskRequestHandler):
    def get(self):
        pubsub.pull_and_publish_event()

def yield_post_jp_event(db_events):
    from mapreduce import context
    ctx = context.get()
    params = ctx.mapreduce_spec.mapper.params
    token_nickname = params.get('token_nickname')
    db_events = [x for x in db_events if x.actual_city_name and x.actual_city_name.endswith('Japan')]
    for db_event in db_events:
        pubsub.eventually_publish_event(db_event.id, token_nickname)

@app.route('/tasks/post_japan_events')
class PostJapanEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        token_nickname = self.request.get('token_nickname', None)
        mapper_params = {
            'entity_kind': 'events.eventdata.DBEvent',
            'handle_batch_size': 20,
            'filters': [('search_time_period', '=', dates.TIME_FUTURE)],
            'token_nickname': token_nickname,
        }
        control.start_map(
            name='Post Future Japan Events',
            reader_spec='mapreduce.input_readers.DatastoreInputReader',
            handler_spec='pubsub.pubsub_tasks.map_post_jp_event',
            shard_count=8, # since we want to stick it in the slow-queue, and don't care how fast it executes
            queue_name='fast-queue',
            mapper_parameters=mapper_params,
        )

@app.route('/tasks/weekly_posts')
class WeeklyEventsPostHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        limit = int(self.request.get('limit', '10'))
        top_cities = cities.get_largest_cities(limit=limit, country='US')
        top_city_keys = [x.key().name() for x in top_cities]
        for city_key in top_city_keys:
            pubsub.eventually_publish_city_key(city_key)
