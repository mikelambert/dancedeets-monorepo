from mapreduce import control

import datetime

from dancedeets import app
from dancedeets import base_servlet
from dancedeets.pubsub import pubsub
from dancedeets.rankings import cities
from dancedeets.search import search_base
from dancedeets.search import search
from dancedeets.util import dates
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
            'entity_kind': 'dancedeets.events.eventdata.DBEvent',
            'handle_batch_size': 20,
            'filters': [('search_time_period', '=', dates.TIME_FUTURE)],
            'token_nickname': token_nickname,
        }
        control.start_map(
            name='Post Future Japan Events',
            reader_spec='mapreduce.input_readers.DatastoreInputReader',
            handler_spec='dancedeets.pubsub.pubsub_tasks.map_post_jp_event',
            shard_count=8,  # since we want to stick it in the slow-queue, and don't care how fast it executes
            queue_name='fast-queue',
            mapper_parameters=mapper_params,
        )


def blacklisted(city):
    if city.country_name == 'US' and city.state_name == 'NY' and city.city_name in [
        'Brooklyn', 'Borough of Queens', 'Manhattan', 'The Bronx'
    ]:
        return True
    return False


@app.route('/tasks/weekly_posts')
class WeeklyEventsPostHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        #TODO: rewrite this to use "top cities" filter from dancedeets.rankings...maybe rewrite our rankings to be better organized?
        limit = int(self.request.get('limit', '10'))
        top_cities = cities.get_largest_cities(limit=limit, country='US')
        top_city_keys = [x.key().name() for x in top_cities if not blacklisted(x)]
        for city_key in top_city_keys:
            pubsub.eventually_publish_city_key(city_key)


def prepare_event_notifications(days, min_attendees, min_dancers, allow_reposting):
    today = datetime.date.today()
    query = search_base.SearchQuery()
    query.start_date = today + datetime.timedelta(days=days)
    query.end_date = today + datetime.timedelta(days=days)
    query.min_attendees = min_attendees
    searcher = search.Search(query)
    results = searcher.get_search_results()
    for result in results:
        pubsub.eventually_publish_event(
            result.event_id,
            post_type=pubsub.POST_TYPE_REMINDER,
            min_attendees=min_attendees,
            min_dancers=min_dancers,
            allow_reposting=allow_reposting
        )


@app.route('/tasks/prepare_event_notifications')
class EventNotificationsHandler(base_servlet.BaseTaskRequestHandler):
    def get(self):
        days = int(self.request.get('days'))
        allow_reposting = self.request.get('allow_reposting') == '1'
        min_attendees = int(self.request.get('min_attendees', '100'))
        min_dancers = int(self.request.get('min_dancers', '40'))
        prepare_event_notifications(days, min_attendees, min_dancers, allow_reposting)
