#!/usr/bin/env python

import logging
import time

import app
import base_servlet
import event_types
from logic import friends
from logic import rsvp
from rankings import cities
from util import urls
from . import onebox
from . import search
from . import search_base
from . import search_pages
from servlets import api


class SearchHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        if not self.request.get('location') and not self.request.get('keywords'):
            return True
        return False

    def get(self, *args, **kwargs):
        self.handle(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.handle(*args, **kwargs)

    def handle(self, city_name=None):
        self.finish_preload()
        if self.user and not self.user.location:
            #TODO(lambert): make this an error
            self.user.add_message("We could not retrieve your location from facebook. Please fill out a location below")
            self.redirect('/user/edit')
            return

        get_data = self.request.GET.copy()
        if get_data.get('start') == '':
            del get_data['start']
        if get_data.get('end') == '':
            del get_data['end']
        form = search_base.SearchForm(get_data, data=self.user.dict_for_form() if self.user else None)
        form.validated = form.validate()
        self.handle_search(form)


@app.route('/calendar/iframe')
class CalendarHandler(SearchHandler):
    template_name = 'calendar_iframe'
    search_class = search.Search

    def handle_search(self, form):
        validated = form.validate()
        if not validated:
            for field, errors in form.errors.items():
                for error in errors:
                    self.add_error(u"%s error: %s" % (getattr(form, field).label.text, error))

        props = dict(query=form.url_params(),)
        self.setup_react_template('calendar.js', props)
        self.render_template(self.template_name)


@app.route('/')
@app.route('/events/relevant')
class RelevantHandler(SearchHandler):
    template_name = 'results'
    search_class = search.Search

    def handle_search(self, form):
        validated = form.validate()
        if not validated:
            for field, errors in form.errors.items():
                for error in errors:
                    self.add_error(u"%s error: %s" % (getattr(form, field).label.text, error))

        if self.request.get('calendar'):
            props = dict(query=form.url_params(),)
            self.setup_react_template('calendar.js', props)
        else:
            search_query = None

            has_more_results = False
            search_results = []
            onebox_links = []
            if validated:
                search_query = form.build_query()

                searcher = self.search_class(search_query)
                if self.indexing_bot:
                    search_results = searcher.get_search_results(full_event=True)
                    search_results = [x for x in search_results if x.db_event.is_indexable()]
                else:
                    initial_result_limit = 1000  # TODO: Make this 20, when the mapreduce finishes
                    searcher.limit = initial_result_limit
                    search_results = searcher.get_search_results()
                    has_more_results = len(search_results) == initial_result_limit

                if 'class' in form.deb.data:
                    from classes import class_index
                    class_results = class_index.ClassSearch(search_query).get_search_results()
                    search_results += class_results
                    search_results.sort(key=lambda x: (x.start_time, x.actual_city_name, x.name))
                onebox_links = onebox.get_links_for_query(search_query)

            geocode = None
            distance = None
            if form.location.data:
                try:
                    geocode, distance = search_base.get_geocode_with_distance(form)
                except:
                    self.add_error('Unknown location: %s' % form.location.data)

            need_full_event = False
            # Keep in sync with mobile react code? And api.py
            skip_people = True
            json_search_response = api.build_search_results_api(
                form, search_query, search_results, (2, 0), need_full_event, geocode, distance, skip_people=skip_people
            )
            props = dict(
                response=json_search_response,
                hasMoreResults=has_more_results,
                showPeople=not skip_people,
                categoryOrder=[''] + [x.public_name for x in event_types.STYLES],
                query=form.url_params(),
            )
            self.setup_react_template('eventSearchResults.js', props)

        self.render_template(self.template_name)


@app.route('/city/(.*)/?')
class CityHandler(RelevantHandler):
    def requires_login(self):
        return False

    def handle(self, city_name):
        # TODO(lambert): Why is this still required, can we get rid of it?
        self.fbl.batch_fetch()  # to avoid bad error handler?
        city_name = city_name.decode('utf-8')
        form = search_base.SearchForm(data={'location': city_name, 'distance': cities.NEARBY_DISTANCE_KM, 'distance_units': 'km'})
        self.handle_search(form)


@app.route('/pages/search')
class RelevantPageHandler(RelevantHandler):
    template_name = 'results_pages'
    search_class = search_pages.SearchPages
