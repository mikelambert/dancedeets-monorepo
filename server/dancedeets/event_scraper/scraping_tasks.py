import app
import base_servlet
from . import auto_add
from . import potential_events_reloading
from . import thing_db
from . import thing_scraper


@app.route('/tools/auto_add_potential_events')
class AutoAddPotentialEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        past_event = self.request.get('past_event', None)
        if past_event == '1':
            past_event = True
        elif past_event == '0':
            past_event = False

        if self.request.get('dancey_only', None) == '1':
            dancey_only = True
        else:
            dancey_only = False

        auto_add.mr_classify_potential_events(self.fbl, past_event, dancey_only)


@app.route('/tools/maybe_add_events')
class MaybeAddEventsHandler(base_servlet.EventIdOperationHandler):
    event_id_operation = staticmethod(auto_add.maybe_add_events)


@app.route('/tasks/count_source_stats')
class CountSourceStatsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        queue = self.request.get('queue', 'slow-queue')
        thing_db.mr_count_potential_events(self.fbl, queue=queue)


@app.route('/tasks/load_potential_events_for_user')
class LoadPotentialEventsForUserHandler(base_servlet.UserIdOperationHandler):
    user_id_operation = staticmethod(potential_events_reloading.load_potential_events_for_user_ids)


@app.route('/tasks/load_all_potential_events')
class LoadAllPotentialEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        # this calls a map function wrapped by mr_user_wrap, so it works correctly on a per-user basis
        potential_events_reloading.mr_load_potential_events(self.fbl)


@app.route('/tasks/load_potential_events_from_wall_posts')
class LoadPotentialEventsFromWallPostsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        min_potential_events = int(self.request.get('min_potential_events', '0'))
        queue = self.request.get('queue', 'slow-queue')
        thing_scraper.mapreduce_scrape_all_sources(self.fbl, min_potential_events=min_potential_events, queue=queue)
