import logging

import app
import base_servlet

@app.route('/_ah/warmup')
class DoNothingHandler(base_servlet.BareBaseRequestHandler):
    def get(self):
        from nlp import event_auto_classifier
        logging.info("Loading regexes")
        event_auto_classifier.build_regexes()
        logging.info("Loaded regexes")
        return
