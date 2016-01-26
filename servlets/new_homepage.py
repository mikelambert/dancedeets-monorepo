
import app
import base_servlet


@app.route(r'/new_homepage')
class ShowEventHandler(base_servlet.BaseRequestHandler):

    def requires_login(self):
        return False

    def get(self):
        self.render_template('new_homepage')