import app
import base_servlet

@app.route('/about')
class AboutHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()
        self.render_template('about')


