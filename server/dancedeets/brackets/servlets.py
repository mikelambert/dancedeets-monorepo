from dancedeets import app
from dancedeets import base_servlet


@app.route('/brackets/')
class RelevantHandler(base_servlet.BaseRequestHandler):
    template_name = 'brackets'

    def get(self):
        props = dict()
        self.setup_react_template('brackets.js', props)
        self.render_template(self.template_name)
