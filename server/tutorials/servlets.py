
import app
import base_servlet


@app.route('/tutorials/([^/]+/[^/]+)$')
class TutorialHandler(base_servlet.BaseRequestHandler):
    def get(self, tutorial_name):
        self.finish_preload()

        props = dict(
            tutorial=tutorial_name,
            loggedIn=bool(self.fb_uid),
            currentLocale=self.locales[0],
        )
        self.setup_react_template('tutorial.js', props)

        self.display['tutorial'] = tutorial_name

        self.render_template('tutorial')

@app.route('/tutorials/(?:([^/]+)/)?$')
class TutorialCategoryHandler(base_servlet.BaseRequestHandler):
    def get(self, style):
        self.finish_preload()

        props = dict(
            style=style,
            loggedIn=bool(self.fb_uid),
            currentLocale=self.locales[0],
        )
        self.setup_react_template('tutorialCategory.js', props)

        self.display['style'] = style

        self.render_template('tutorial_category')
