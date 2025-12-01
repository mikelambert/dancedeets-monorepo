"""
Social publishing task handlers.

The batch posting of Japan events has been migrated to Cloud Run Jobs.
See: dancedeets.jobs.post_japan_events

This module retains:
- SocialPublisherHandler: Pulls and publishes events from pubsub queue
- WeeklyEventsPostHandler: Posts weekly events for top US cities
- EventNotificationsHandler: Prepares event reminder notifications
"""
import datetime

from dancedeets import app
from dancedeets import base_servlet
from dancedeets.pubsub import pubsub
from dancedeets.rankings import cities_db
from dancedeets.search import search_base
from dancedeets.search import search
from . import pubsub


@app.route('/tasks/social_publisher')
class SocialPublisherHandler(base_servlet.BaseTaskRequestHandler):
    def get(self):
        pubsub.pull_and_publish_event()


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
        top_cities = cities_db.get_largest_cities(limit=limit, country='US')
        top_city_keys = [x.geoname_id for x in top_cities if not blacklisted(x)]
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
