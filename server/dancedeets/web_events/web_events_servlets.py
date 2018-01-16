import json
import logging
from dancedeets import keys
import urllib
import scrapinghub
import webapp2

from dancedeets import app
from dancedeets.event_scraper import add_entities


class JsonDataHandler(webapp2.RequestHandler):
    def initialize(self, request, response):
        super(JsonDataHandler, self).initialize(request, response)

        if self.request.body:
            escaped_body = urllib.unquote_plus(self.request.body.strip('='))
            self.json_body = json.loads(escaped_body)
        else:
            self.json_body = None


@app.route('/web_events/upload_multi')
class WebMultiUploadHandler(JsonDataHandler):
    def post(self):
        if self.json_body['scrapinghub_key'] != keys.get('scrapinghub_key'):
            self.response.status = 403
            return
        for json_body in self.json_body['items']:
            add_entities.add_update_web_event(json_body)

        self.response.status = 200


def get_spiders():
    return [
        'EnterTheStage',
        'Dews',
        'StreetDanceKorea',
        'ComeOn5678',
        'TokyoDanceLife',
        'BBoyBattles',
        'DanceDelight',
    ]


def get_shub_project():
    conn = scrapinghub.Connection(keys.get('scrapinghub_key'))
    project = scrapinghub.Project(conn, 27474)
    return project


def start_spiders(spiders):
    project = get_shub_project()
    job_keys = []
    for spider in spiders:
        job_id = project.schedule(spider)
        job_keys.append(job_id)
    logging.info("Scheduled jobs: %s", job_keys)
    return job_keys


@app.route('/tasks/web_events/start_spiders')
class MemoryUsers(webapp2.RequestHandler):
    def get(self):
        start_spiders(get_spiders())

    post = get
