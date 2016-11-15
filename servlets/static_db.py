import logging
import markdown

from google.appengine.ext import ndb

import app
import base_servlet

class StaticContent(ndb.Model):
    # SSO
    name = ndb.StringProperty()
    language = ndb.StringProperty()

    title = ndb.TextProperty()
    markdown = ndb.TextProperty()

@app.route('/t/(.*)')
class DbStaticHandler(base_servlet.BaseRequestHandler):
    def requires_login(self):
        return False

    def get(self, name):
        self.finish_preload()
        contents = StaticContent.query(StaticContent.name == name).fetch(100)
        if not contents:
            self.response.status = 404
            return
        if len(contents) > 1:
            self.response.status = 500
            logging.error('Found too many StaticContentPages: %s', contents)
            return
        content = contents[0]

        rendered_content = markdown.markdown(content.markdown)
        self.display['title'] = content.title
        self.display['content'] = rendered_content
        self.render_template('static_wrapper')
