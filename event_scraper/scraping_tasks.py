import logging

import base_servlet
import fb_api
from logic import backgrounder
from . import auto_add
from . import potential_events_reloading
from . import thing_db
from . import thing_scraper


class AutoAddPotentialEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        past_event = self.request.get('past_event', None)
        if past_event == '1':
            past_event = True
        elif past_event == '0':
            past_event = False
        auto_add.mr_classify_potential_events(self.fbl, past_event)

class ExportSourcesHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        queue = self.request.get('queue', 'fast-queue')
        thing_db.mapreduce_export_sources(self.fbl, queue=queue)

class LoadPotentialEventsForUserHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        user_ids = [x for x in self.request.get('user_ids').split(',') if x]
        potential_events_reloading.load_potential_events_for_user_ids(self.fbl, user_ids)

class LoadAllPotentialEventsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        # this calls a map function wrapped by mr_user_wrap, so it works correctly on a per-user basis
        potential_events_reloading.mr_load_potential_events(self.fbl)

class LoadPotentialEventsFromWallPostsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        min_potential_events = int(self.request.get('min_potential_events', '0'))
        queue = self.request.get('queue', 'super-slow-queue')
        thing_scraper.mapreduce_scrape_all_sources(self.fbl, min_potential_events=min_potential_events, queue=queue)

class LoadPotentialEventsForFriendsHandler(base_servlet.BaseTaskFacebookRequestHandler):
    def get(self):
        friend_lists = []
        #TODO(lambert): extract this out into some sort of dynamic lookup based on Mike Lambert
        friend_lists.append('530448100598') # Freestyle SF
        friend_lists.append('565645040648') # Freestyle NYC
        friend_lists.append('10100136378543108') # Freestyle Asia
        friend_lists.append('10100415076510148') # Freestyle Boston
        friend_lists.append('734193578028') # Freestyle Japan
        friend_lists.append('612289903968') # Freestyle Socal
        friend_lists.append('646041540418') # Freestyle Europe
        friend_lists.append('583877258138') # Freestyle Elsewhere
        friend_lists.append('565645070588') # Choreo SF
        friend_lists.append('556389713398') # Choreo LA
        friend_lists.append('565645155418') # Choreo Elsewhere
        print self.fbl.access_token
        for fl_id, fl in zip(friend_lists, self.fbl.get_multi(fb_api.LookupFriendList, friend_lists, allow_cache=False)):
            logging.info("Friend list %s: Searching %s friends for events", fl_id, len(fl['friend_list']['data']))
            friend_ids = [x['id'] for x in fl['friend_list']['data']]
            backgrounder.load_potential_events_for_friends(self.fb_uid, friend_ids, allow_cache=self.allow_cache)
