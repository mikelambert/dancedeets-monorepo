import logging
import mimetypes
import os
import re

import app
import base_servlet

mappings = [
    (r'^/(dancedeets\.png)', './'),
    (r'^/(robots\.txt)', './'),
    (r'^/(favicon\.ico)', './'),
    (r'^/v?css/(.*)', 'css/'),
    (r'^/v?js/(.*)', 'js/'),
    (r'^/dist[^/]*/(.*)', 'dist/'),
    (r'^/images/(.*)', 'images/'),
    (r'^/mapreduce/pipeline/images/(.*)', 'mapreduce/pipeline/ui/images/')
]

compiled_mappings = [(re.compile(regex), path) for regex, path in mappings]
all_static = '|'.join(regex for regex, path in mappings)


@app.route(all_static)
class StaticHandler(base_servlet.webapp2.RequestHandler):
    def get(self, *args):
        for regex, path in compiled_mappings:
            result = regex.match(self.request.path)
            if result:
                full_path = os.path.join(path, result.group(1))
                if os.path.exists(full_path):
                    mimetype, encoding = mimetypes.guess_type(self.request.path)
                    self.response.headers['Content-Type'] = mimetype
                    self.response.out.write(open(full_path).read())
                else:
                    self.response.set_status(404)
