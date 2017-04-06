import webapp2

import app

@app.route('/_ah/start')
class StartHandler(webapp2.RequestHandler):
    def get(self):
        pass

@app.route('/_ah/stop')
class StopHandler(webapp2.RequestHandler):
    def get(self):
        pass
