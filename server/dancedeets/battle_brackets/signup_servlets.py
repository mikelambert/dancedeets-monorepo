import random
from firebase import firebase
import time

from dancedeets import keys
from dancedeets.servlets import api

auth = firebase.FirebaseAuthentication(keys.get('firebase_secret'), None)
db = firebase.FirebaseApplication('https://dancedeets-hrd.firebaseio.com', auth)
#result = db.get('/events', None)
#print result


@api.apiroute(r'/event_signups/register')
class RegisterHandler(api.ApiHandler):
    supports_auth = True

    def post(self):
        event_id = self.json_body.get('event_id')
        category_id = self.json_body.get('category_id')
        team = self.json_body.get('team')
        team_name = team.get('team_name')

        dancers = []
        dancer_index = 1
        while team.get('dancer_name_%s' % dancer_index):
            dancer_name = team.get('dancer_name_%s' % dancer_index)
            dancer_id = team.get('dancer_id_%s' % dancer_index) or dancer_name
            dancers.append({'name': dancer_name, 'id': dancer_id})
            dancer_index += 1

        event = db.get('/events', event_id)
        category_index = [index for (index, elem) in enumerate(event['categories']) if elem['id'] == category_id][0]

        signup_id = '%s_%s' % (int(time.time()), random.randint(10000, 99999))
        signup = {
            'id': signup_id,
            'teamName': team_name,
            'dancers': dancers,
        }
        db.put('/events/%s/categories/%s/signups/' % (event_id, category_index), signup_id, signup)
        self.write_json_success()


@api.apiroute(r'/event_signups/unregister')
class UnregisterHandler(api.ApiHandler):
    supports_auth = True

    def post(self):
        event_id = self.json_body.get('event_id')
        category_id = self.json_body.get('category_id')
        signup_id = self.json_body.get('signup_id')

        event = db.get('/events', event_id)
        category_index = [index for (index, elem) in enumerate(event['categories']) if elem['id'] == category_id][0]
        signup = event['categories'][category_index]['signups'][signup_id]
        authenticated = self.fb_uid in signup['dancers']
        if authenticated:
            db.delete('/events/%s/categories/%s/signups' % (event_id, category_index), signup_id)
            self.write_json_success()
        else:
            self.write_json_error('not authorized to delete signup')
