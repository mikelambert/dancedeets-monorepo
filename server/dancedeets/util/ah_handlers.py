from dancedeets import app
from dancedeets.util.flask_adapter import BaseHandler


@app.route('/_ah/start')
class StartHandler(BaseHandler):
    def get(self):
        pass


@app.route('/_ah/stop')
class StopHandler(BaseHandler):
    def get(self):
        pass
