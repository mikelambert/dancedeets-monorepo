import json
import logging
from dancedeets import keys
import urllib.parse
import scrapinghub

from dancedeets import app
from dancedeets.event_scraper import add_entities
from dancedeets.util.flask_adapter import BaseHandler


class JsonDataHandler(BaseHandler):
    def initialize(self, flask_req, flask_app):
        super(JsonDataHandler, self).initialize(flask_req, flask_app)

        if self.request.body:
            body_str = self.request.body.decode('utf-8') if isinstance(self.request.body, bytes) else self.request.body
            escaped_body = urllib.parse.unquote_plus(body_str.strip('='))
            self.json_body = json.loads(escaped_body)
        else:
            self.json_body = None


@app.route('/web_events/upload_multi')
class WebMultiUploadHandler(JsonDataHandler):
    def post(self):
        if self.json_body['scrapinghub_key'] != keys.get('scrapinghub_key'):
            self.response.set_status(403)
            return
        for json_body in self.json_body['items']:
            add_entities.add_update_web_event(json_body)

        self.response.set_status(200)


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
class StartSpidersHandler(BaseHandler):
    def get(self):
        start_spiders(get_spiders())

    post = get
