import datetime
import json
import logging
import keys
import urllib
import webapp2

import app
import base_servlet
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

    def make_class(index, result):
        result = {
            'url': result.source_page,
            'name': result.name,
            'location': result.actual_city_name,
            'startTime': result.start_time_raw,
            'categories': result.extended_categories(),
            'key': 'result-' + index,
        }
        if result.sponsor:
            result['sponsor'] = result.sponsor
        return result

    def handle(self, location):
        self.finish_preload()

        if location not in ['nyc', 'la']:
            self.add_error('Bad location: %s' % location)
        full_location = self.location_shortcuts.get(location, location)
        self.errors_are_fatal
        form = search_base.SearchForm(
            start=datetime.date.today() - datetime.timedelta(days=1),
            end=datetime.date.today() + datetime.timedelta(days=7),
            location=full_location,
        )
        search_results = class_index.ClassSearch(form.build_query(start_end_query=True)).get_search_results()

        self.display['classes'] = [self.make_class(i, x) for i, x in enumerate(search_results)]
        self.display['location'] = location
        self.display['full_location'] = full_location
        self.render_template(self.template_name)


class JsonDataHandler(webapp2.RequestHandler):
    def initialize(self, request, response):
        super(JsonDataHandler, self).initialize(request, response)

        if self.request.body:
            escaped_body = urllib.unquote_plus(self.request.body.strip('='))
            self.json_body = json.loads(escaped_body)
        else:
            self.json_body = None


def process_uploaded_item(json_body):
    #TODO: And maybe only save/reindex if there were legit changes?
    for key, value in json_body.iteritems():
        if key in ['start_time', 'end_time', 'scrape_time']:
            json_body[key] = datetime.datetime.strptime(value, DATETIME_FORMAT)
    studio_class = class_models.StudioClass(**json_body)
    studio_class.put()
    logging.info("Saving %s with scrape_time %s", studio_class.key, studio_class.scrape_time)


def process_upload_finalization(studio_name):
    logging.info('De-duping all classes for %s', studio_name)
    historical_fixup = datetime.datetime.today() - datetime.timedelta(days=2)
    # TODO: sometimes this query returns stale data. In particular,
    # it returns objects that don't have the latest updated scrape_time.
    # This then confuses dedupe_classes() logic, which wants to delete
    # these presumed-dead classes, when in fact they are still alive.
    # Disabling the memcache and incontext NDB caches doesn't appear to help,
    # since the stale objects are returned from the dev_apperver DB directly.
    query = class_models.StudioClass.query(
        class_models.StudioClass.studio_name == studio_name,
        class_models.StudioClass.start_time >= historical_fixup)
    num_events = 1000
    results = query.fetch(num_events)
    if len(results) == num_events:
        logging.error("Processing %s events for studio %s, and did not reach the end of days-with-duplicates", num_events, studio_name)

    max_scrape_time = max(results, key=lambda x: x.scrape_time).scrape_time

    classes_by_date = {}
    for studio_class in results:
        classes_by_date.setdefault(studio_class.start_time.date(), []).append(studio_class)
    for date, classes in classes_by_date.iteritems():
        # RISKY!!! uses current date (in what timezone??)
        if date < datetime.date.today():
            scrape_time_to_keep = max(classes, key=lambda x: x.scrape_time).scrape_time
        else:
            scrape_time_to_keep = max_scrape_time
        logging.info('Date %s: ScrapeTime To Keep %s: %s classes', date, scrape_time_to_keep, len(classes))
        dedupe_classes(scrape_time_to_keep, classes)


@app.route('/classes/upload_multi')
class ClassMultiUploadHandler(JsonDataHandler):
    def post(self):
        if self.json_body['scrapinghub_key'] != keys.get('scrapinghub_key'):
            self.response.status = 403
            return
        for item in self.json_body['items']:
            logging.info('Processing %s', item)
            process_uploaded_item(item)
        process_upload_finalization(self.json_body['studio_name'])
        self.response.status = 200


def dedupe_classes(most_recent_scrape_time, classes):
    """Returns true if there were classes de-duped, or empty classes and we don't know.
    Returns false once we get a full day of classes without dupes."""
    if not classes:
        return True
    logging.info('De-duping %s classes on %s' % (len(classes), classes[0].start_time.date()))
    logging.info('Assuming most recent scrape time is %s', most_recent_scrape_time)
    class_scrape_times = set(x.scrape_time for x in classes)
    logging.info('Class scrape times are: %s', class_scrape_times)
    old_classes = [x for x in classes if x.scrape_time != most_recent_scrape_time]
    logging.info('Found %s old classes', len(old_classes))
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
        class_index.StudioClassIndex.rebuild_from_query(force=True)
        self.response.status = 200
    get=post


@app.route('/classes/finish_upload')
class ClassFinishUploadhandler(JsonDataHandler):
    def post(self):
        studio_name = self.request.get('studio_name') or self.json_body['studio_name']
        if not studio_name:
            return
        process_upload_finalization(studio_name)
        self.response.status = 200
    get=post
# TODO: We need to optionally return these in the API
# TODO: We need the api clients to be able to display class data
