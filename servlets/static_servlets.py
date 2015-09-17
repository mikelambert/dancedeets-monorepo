import app
import base_servlet

@app.route('/help')
class HelpHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()
        if self.request.get('hl') == 'ko':
            self.render_template('help_korea')
        else:
            self.render_template('help')

@app.route('/privacy')
class PrivacyHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()
        self.render_template('privacy')

@app.route('/about')
class AboutHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()
        self.render_template('about')




