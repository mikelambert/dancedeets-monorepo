import datetime
import json
import logging
import keys
import urllib
import webapp2

import app
from events import eventdata
from events import event_updates


class JsonDataHandler(webapp2.RequestHandler):
    def initialize(self, request, response):
        super(JsonDataHandler, self).initialize(request, response)

        if self.request.body:
            escaped_body = urllib.unquote_plus(self.request.body.strip('='))
            self.json_body = json.loads(escaped_body)
        else:
            self.json_body = None


def process_uploaded_item(json_body):
    return e


def process_upload_finalization(studio_name):
    logging.info('De-duping all classes for %s', studio_name)
    historical_fixup = datetime.datetime.today() - datetime.timedelta(days=2)
    # TODO: sometimes this query returns stale data. In particular,
    # it returns objects that don't have the latest updated scrape_time.
    # This then confuses dedupe_classes() logic, which wants to delete
    # these presumed-dead classes, when in fact they are still alive.
    # Disabling the memcache and incontext NDB caches doesn't appear to help,
    # since the stale objects are returned from the dev_apperver DB directly.
    query = None
    #class_models.StudioClass.query(
    #    class_models.StudioClass.studio_name == studio_name,
    #    class_models.StudioClass.start_time >= historical_fixup)
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
        print date, scrape_time_to_keep, classes
        # dedupe_classes(scrape_time_to_keep, classes)


@app.route('/web_events/upload_multi')
class ClassMultiUploadHandler(JsonDataHandler):
    def post(self):
        if self.json_body['scrapinghub_key'] != keys.get('scrapinghub_key'):
            self.response.status = 403
            return
        events_to_update = []
        for json_body in self.json_body['items']:
            event_id = eventdata.DBEvent.generate_id(json_body['namespace'], json_body['namespaced_id'])
            e = eventdata.DBEvent.get_or_insert(event_id)
            events_to_update.append((e, json_body))
        event_updates.update_and_save_web_events(events_to_update)
        process_upload_finalization(self.json_body['studio_name'])
        self.response.status = 200
