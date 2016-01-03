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
        expiry_days = int(self.request.get('expiry_days', 0)) or None
        auto_add.mr_classify_potential_events(self.fbl, past_event, expiry_days)

@app.route('/tools/export_sources')
class ExportSourcesHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        queue = self.request.get('queue', 'fast-queue')
        thing_db.mapreduce_export_sources(self.fbl, queue=queue)

@app.route('/tasks/count_source_stats')
class CountSourceStatsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        queue = self.request.get('queue', 'slow-queue')
        thing_db.mr_count_potential_events(self.fbl, queue=queue)

@app.route('/tasks/load_potential_events_for_user')
class LoadPotentialEventsForUserHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        user_ids = [x for x in self.request.get('user_ids').split(',') if x]
        potential_events_reloading.load_potential_events_for_user_ids(self.fbl, user_ids)

@app.route('/tasks/load_all_potential_events')
class LoadAllPotentialEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        # this calls a map function wrapped by mr_user_wrap, so it works correctly on a per-user basis
        potential_events_reloading.mr_load_potential_events(self.fbl)

@app.route('/tasks/load_potential_events_from_wall_posts')
class LoadPotentialEventsFromWallPostsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        min_potential_events = int(self.request.get('min_potential_events', '0'))
        queue = self.request.get('queue', 'super-slow-queue')
        thing_scraper.mapreduce_scrape_all_sources(self.fbl, min_potential_events=min_potential_events, queue=queue)
