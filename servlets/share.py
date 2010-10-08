import base_servlet

class ShareHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        self.render_template('share')

