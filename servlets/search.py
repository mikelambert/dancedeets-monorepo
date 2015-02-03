#!/usr/bin/env python

import logging
import time
import urllib

import base_servlet
from events import eventdata
from logic import rankings
from logic import friends
from logic import rsvp
from logic import search
from logic import search_base
from util import timings

class RelevantHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        if not self.request.get('location') and not self.request.get('city_name'):
            return True
        return False

    def get(self):
        self.handle()

    def post(self):
        self.handle()

    @timings.timed
    def handle(self, city_name=None):
        self.finish_preload()
        if self.user and not self.user.location:
            #TODO(lambert): make this an error
            self.user.add_message("We could not retrieve your location from facebook. Please fill out a location below")
            self.redirect('/user/edit')
            return

        fe_search_query = search_base.FrontendSearchQuery.create_from_request_and_user(self.request, self.user, city_name=city_name)
        validation_errors = fe_search_query.validation_errors()
        if validation_errors:
            self.add_error('Invalid search query: %s' % ', '.join(validation_errors))

        if not self.request.get('calendar'):
            search_query = search.SearchQuery.create_from_query(fe_search_query)
            if fe_search_query.validated:
                search_results = search_query.get_search_results(self.fbl)
            else:
                search_results = []
            # We can probably speed this up 2x by shrinking the size of the fb-event-attending objects. a list of {u'id': u'100001860311009', u'name': u'Dance InMinistry', u'rsvp_status': u'attending'} is 50% overkill.
            a = time.time()
            friends.decorate_with_friends(self.fbl, search_results)
            logging.info("Decorating with friends-attending took %s seconds", time.time() - a)
            a = time.time()
            rsvp.decorate_with_rsvps(self.fbl, search_results)
            logging.info("Decorating with personal rsvp data took %s seconds", time.time() - a)

            if self.request.get('fake') == '1':
                import fb_api
                fb_event = self.fbl.get(fb_api.LookupEvent, '229831487172739')
                from google.appengine.api import search as search_api

                doc = search_api.Document(
                    doc_id=str(fb_event['info']['id']),
                    fields=[
                        search_api.TextField(name='event_keywords', value='dance, competition'),
                        search_api.TextField(name='actual_city_name', value='New York, NY'),
                    ],
                )
                pseudo_db_event = search.PseudoDBEvent(doc)
                result = search.SearchResult(pseudo_db_event, fb_event)
                result.attendee_count = 100
                result.attending_friend_count = 2
                result.attending_friends = ['Mike', 'John']
                import datetime
                result.start_time = datetime.datetime.now()
                result.end_time = datetime.datetime.now() + datetime.timedelta(days=2)
                search_results = [result]

            past_results, present_results, grouped_results = search.group_results(search_results)
            if search_query.time_period == eventdata.TIME_FUTURE:
                present_results = past_results + present_results
                past_results = []

            self.display['num_upcoming_results'] = sum([len(x.results) for x in grouped_results]) + len(present_results)
            self.display['past_results'] = past_results
            self.display['ongoing_results'] = present_results
            self.display['grouped_upcoming_results'] = grouped_results

        if fe_search_query.past:
            self.display['selected_tab'] = 'past'
        elif self.request.get('calendar'):
            self.display['selected_tab'] = 'calendar'
        else:
            self.display['selected_tab'] = 'present'

        a = time.time()
        ranking_location = rankings.get_ranking_location(fe_search_query.location)
        logging.info("computing largest nearby city took %s seconds", time.time() - a)

        a = time.time()
        #TODO(lambert): perhaps produce optimized versions of these without styles/times, for use on the homepage? less pickling/loading required
        event_top_n_cities, event_selected_n_cities = rankings.top_n_with_selected(rankings.get_thing_ranking(rankings.get_city_by_event_rankings(), rankings.ALL_TIME), ranking_location)
        user_top_n_cities, user_selected_n_cities = rankings.top_n_with_selected(rankings.get_thing_ranking(rankings.get_city_by_user_rankings(), rankings.ALL_TIME), ranking_location)
        logging.info("Sorting and ranking top-N cities took %s seconds", time.time() - a)

        self.display['user_top_n_cities'] = user_top_n_cities
        self.display['event_top_n_cities'] = event_top_n_cities
        self.display['user_selected_n_cities'] = user_selected_n_cities
        self.display['event_selected_n_cities'] = event_selected_n_cities

        self.display['defaults'] = fe_search_query
        self.display['display_location'] = fe_search_query.location

        request_params = fe_search_query.url_params()
        if 'calendar' in request_params:
            del request_params['calendar'] #TODO(lambert): clean this up more
        if 'past' in request_params:
            del request_params['past'] #TODO(lambert): clean this up more
        self.display['past_view_url'] = '/events/relevant?past=1&%s' % '&'.join('%s=%s' % (k, v) for (k, v) in request_params.iteritems())
        self.display['upcoming_view_url'] = '/events/relevant?%s' % '&'.join('%s=%s' % (k, v) for (k, v) in request_params.iteritems())
        self.display['calendar_view_url'] = '/events/relevant?calendar=1&%s' % '&'.join('%s=%s' % (k, v) for (k, v) in request_params.iteritems())
        self.display['calendar_feed_url'] = '/calendar/feed?%s' % '&'.join('%s=%s' % (k, v) for (k, v) in request_params.iteritems())

        self.display['CHOOSE_RSVPS'] = eventdata.CHOOSE_RSVPS
        self.render_template('results')

class CityHandler(RelevantHandler):
    def requires_login(self):
        return False

    def handle(self):
        path_bits = self.request.path.split('/')
        city_name = urllib.unquote(path_bits[2])

        # if they only care about particular types, too bad, redirect them to the main page since we don't support that anymore
        if len(path_bits) >= 4:
            self.redirect('/'.join(path_bits[:-1]))
            return

        super(CityHandler, self).handle(city_name=city_name)
