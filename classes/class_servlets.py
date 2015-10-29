import datetime
import json
import logging
import urllib
import webapp2

import app
import base_servlet
from loc import gmaps_api
from loc import math
from search import search_base
from . import class_index
from . import class_models

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


@app.route('/classes/(nyc|la)')
class RelevantHandler(base_servlet.BaseRequestHandler):
    template_name = 'class-results'

    location_shortcuts = {
        'nyc': 'New York, NY',
        'la': 'Los Angeles, CA',
    }

    def requires_login(self):
        return False

    def get(self, *args, **kwargs):
        self.handle(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.handle(*args, **kwargs)

    def handle(self, location):
        self.finish_preload()

        if location not in ['nyc', 'la']:
            self.add_error('Bad location: %s' % location)
        location = self.location_shortcuts.get(location, location)
        self.errors_are_fatal
        form = search_base.SearchForm(
            start=datetime.date.today(),
            end=datetime.date.today() + datetime.timedelta(days=7),
            location=location,
            )
        search_results = class_index.ClassSearch(form.build_query()).get_search_results()

        self.display['search_results'] = search_results
        self.display['location'] = location
        webview = bool(self.request.get('webview'))
        self.display['webview'] = webview
        if webview:
            self.display['class_base_template'] = '_base_webview.html'
        else:
            self.display['class_base_template'] = '_base.html'
        self.render_template(self.template_name)



class JsonDataHandler(webapp2.RequestHandler):
    def initialize(self, request, response):
        super(JsonDataHandler, self).initialize(request, response)

        if self.request.body:
            escaped_body = urllib.unquote_plus(self.request.body.strip('='))
            self.json_body = json.loads(escaped_body)
        else:
            self.json_body = None


@app.route('/classes/upload')
class ClassUploadHandler(JsonDataHandler):
    def post(self):
        #TODO: check if class already exists, and update it versus creating a new one?
        #TODO: And maybe only save/reindex if there were legit changes?
        for key, value in self.json_body.iteritems():
            if key in ['start_time', 'end_time', 'scrape_time']:
                self.json_body[key] = datetime.datetime.strptime(value, DATETIME_FORMAT)
        studio_class = class_models.StudioClass(**self.json_body)
        studio_class.put()
        logging.info("Saving %s with scrape_time %s", studio_class.key, studio_class.scrape_time)
        self.response.status = 200

def dedupe_classes(classes):
    """Returns true if there were classes de-duped, or empty classes and we don't know.
    Returns false once we get a full day of classes without dupes."""
    if not classes:
        return True
    logging.info('De-duping %s classes on %s' %(len(classes), classes[0].start_time.date()))
    most_recent_scrape_time = max(x.scrape_time for x in classes)
    old_classes = [x for x in classes if x.scrape_time != most_recent_scrape_time]
    deleted = 0
    for x in old_classes:
        # See the note down below next to the StudioClass.query().
        # That query returns stale data, so we double-check the scrape time here.
        # It's inefficient, but only a small percentage of cases
        # should run through this code, so performance shouldn't be affected.
        # Also in order for this to work, the in-process context cache
        # must be disabled (via StudioClass._use_cache) so that it uses a fresh DB,
        # instead of the stale in-process cache populated from the stale query.
        old_class = x.key.get()
        if old_class.scrape_time != most_recent_scrape_time:
            x.key.delete()
            deleted += 1
        else:
            logging.error("Found stale data! Went to delete stale class %s due to old scrape_time %s, but it is actually %s", x.key, x.scrape_time, old_class.scrape_time)
    logging.info("Kept %s classes.", len(classes) - deleted)
    return bool(old_classes)


@app.route('/classes/reindex')
class ClassReIndexHandler(JsonDataHandler):
    def post(self):
        for cls in class_models.StudioClass.query().fetch(10000):
            if not cls.latitude:
                cls.key.delete()

        class_index.StudioClassIndex.rebuild_from_query()
        self.response.status = 200
    get=post

@app.route('/classes/finish_upload')
class ClassFinishUploadhandler(JsonDataHandler):
    def post(self):
        #studio_name = self.json_body['studio_name']
        studio_name = self.request.get('studio_name') or self.json_body['studio_name']
        if not studio_name:
            return
        logging.info('De-duping all classes for %s', studio_name)
        historical_fixup = datetime.datetime.today() - datetime.timedelta(days=2)
        # TODO: sometimes this query returns stale data. In particular,
        # it returns objects that don't have the latest updated scrape_time.
        # This then confuses dedupe_classes() logic, which wants to delete
        # these presumed-dead classes, when in fact they are still alive.
        # Disabling the memcache and incontext NDB caches doesn't appear to help,
        # since the stale objects are returned from the dev_apperver DB directly.
        query = class_models.StudioClass.query(
            class_models.StudioClass.studio_name==studio_name,
            class_models.StudioClass.start_time >= historical_fixup)
        #TODO: why does this sort not work??
        # query = query.order(-class_models.StudioClass.start_time)
        num_events = 1000
        results = query.fetch(num_events)
        results = sorted(results, key=lambda x: x.start_time, reverse=True)
        if len(results) == num_events:
            logging.error("Processing %s events for studio %s, and did not reach the end of days-with-duplicates", num_events, studio_name)
        classes_on_date = []
        processing_date = None
        for studio_class in results:
            class_date = studio_class.start_time.date()
            if class_date == processing_date:
                classes_on_date.append(studio_class)
            else:
                dedupe_classes(classes_on_date)
                processing_date = class_date
                classes_on_date = [studio_class]
        dedupe_classes(classes_on_date)
        self.response.status = 200
    get=post
# TODO: We need to optionally return these in the API
# TODO: We need the api clients to be able to display class data
