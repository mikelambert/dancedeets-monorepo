import json

import app
import base_servlet
from loc import gmaps_api
import keys


@app.route('/_gmaps_api')
class ClassMultiUploadHandler(base_servlet.JsonDataHandler):
    def post(self):
        if self.json_body['private_key'] != keys.get('private_key'):
            self.response.status = 403
            return

        lookup_type = self.json_body['lookup_type']
        lookup_kwargs = self.json_body['lookup']
        if lookup_type == 'places':
            result = gmaps_api.places_api.get_json(**lookup_kwargs)
        elif lookup_type == 'geocode':
            result = gmaps_api.geocode_api.get_json(**lookup_kwargs)
        else:
            self.response.status = 404
            return

        self.response.write(json.dumps(result))
