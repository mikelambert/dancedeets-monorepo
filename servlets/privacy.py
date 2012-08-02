import base_servlet

class PrivacyHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()
        self.render_template('privacy')


