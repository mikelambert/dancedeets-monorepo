from dancedeets import app
from dancedeets import base_servlet


@app.route('/tutorials/([^/]+)/([^/]+)$')
class TutorialHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self, style, tutorial_id):
        self.finish_preload()

        tutorial_name = f"{style}/{tutorial_id}"
        props = dict(tutorial=tutorial_name,)
        self.setup_react_template('tutorial.js', props)

        self.display['tutorial'] = tutorial_name

        self.render_template('tutorial')


@app.route('/tutorials$')
class TutorialRedirectHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()
        self.redirect('/tutorials/')


# Handle /tutorials/ (with trailing slash, no style)
@app.route('/tutorials/$')
class TutorialCategoryIndexHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self):
        self.finish_preload()

        props = dict(style=None,)
        self.setup_react_template('tutorialCategory.js', props)

        self.display['style'] = None

        self.render_template('tutorial_category')


# Handle /tutorials/<style> and /tutorials/<style>/
@app.route('/tutorials/([^/]+)/?$')
class TutorialCategoryHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self, style):
        self.finish_preload()

        props = dict(style=style,)
        self.setup_react_template('tutorialCategory.js', props)

        self.display['style'] = style

        self.render_template('tutorial_category')
