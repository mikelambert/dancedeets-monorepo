import base_servlet

class AboutHandler(base_servlet.BaseRequestHandler):
    def get(self):
        self.finish_preload()
        self.render_template('about')


