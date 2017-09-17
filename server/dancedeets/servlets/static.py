import mimetypes
import os
import re
import webapp2

from dancedeets import app

mappings = [(r'^/(dancedeets\.png)', './'), (r'^/(robots\.txt)', './'), (r'^/(favicon\.ico)', './'), (r'^/v?css/(.*)', 'css/'),
            (r'^/v?js/(.*)', 'js/'), (r'^/dist[^/]*/(.*)', 'dist/'), (r'^/images/(.*)', 'images/'),
            (r'^/mapreduce/pipeline/images/(.*)', 'mapreduce/pipeline/ui/images/')]

compiled_mappings = [(re.compile(regex), path) for regex, path in mappings]
all_static = '|'.join(regex for regex, path in mappings)

mimetypes.add_type('application/font-woff2', '.woff2')


@app.route(all_static)
class StaticHandler(webapp2.RequestHandler):
    def get(self, *args):
        for regex, path in compiled_mappings:
            result = regex.match(self.request.path)
            if result:
                full_path = os.path.join(path, result.group(1))
                if os.path.isfile(full_path):
                    mimetype, encoding = mimetypes.guess_type(self.request.path)
                    if mimetype:
                        self.response.headers['Content-Type'] = mimetype
                    # Only do this on prod, let dev remain uncached
                    if self.request.app.prod_mode:
                        self.response.headers['Cache-Control'] = 'public, max-age=%s' % (7 * 24 * 60 * 60)
                        self.response.headers['Vary'] = 'Accept-Encoding'
                    self.response.out.write(open(full_path).read())
                else:
                    self.response.set_status(404)
