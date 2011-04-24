import urllib2
import csv
import string
import StringIO
from django.utils import simplejson

from events import eventdata
from events import tags

trans = string.maketrans("-/","  ")
delchars = string.punctuation.replace("-", "").replace("/", "")
def strip_punctuation(s):
        return s.translate(trans, delchars)

def get_training_features(real_fb_event): 
    if 'owner' in real_fb_event['info']: 
        owner_name = real_fb_event['info']['owner']['id'] 
    else: 
        owner_name = '' 
    location = eventdata.get_original_address_for_event(real_fb_event).encode('utf8')
    name_and_description = '%s %s' % (real_fb_event['info']['name'], real_fb_event['info'].get('description', '')) 
    name_and_description = name_and_description.replace('\n', ' ').encode('utf8') 
    return owner_name, strip_punctuation(location).lower(), strip_punctuation(name_and_description).lower()

# The regular access key does not work like the docs say, escalated but waiting to hear back
def broken_predict_types_for_event(fb_event):
    google_key = file("training/googlekey", 'r').read().strip()
    event_types = [x[0] for x in tags.FREESTYLE_EVENT_LIST + tags.CHOREO_EVENT_LIST]
    print 'Content-type: text/plain\n\n'
    for event_type in event_types:
        model = 'dancedeets%%2Ftraining_csv-%s.txt' % event_type
        predict_url = "https://www.googleapis.com/prediction/v1.2/training/%s/predict?key=%s" % (model, google_key)
        training_features = get_training_features(fb_event)
        post_data = simplejson.dumps({'input': {'csvInstance': training_features}})
        print post_data
        print predict_url
        prediction_results_text = urllib2.urlopen(predict_url, post_data).read()
        print prediction_results_text
        prediction_results = simplejson.loads(prediction_results_text)
        print prediction_results
        #print event_type, prediction_results

# instead let's do things with oauth with this ugly token we need to keep renewing
import httplib2
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.tools import run

def predict_types_for_event(fb_event):
    # This is broken because we need to *write* to this
    storage = Storage('prediction.dat')
    credentials = storage.get()
    # So maybe it's better to do something like this, except that initializing this is hard because it wants a web auth flow
    # credentials = StorageByKeyName(Credentials, user.user_id(), 'credentials').get()
    # So yeah, for now this is broken too...
    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build("prediction", "v1.2", http=http)

    event_types = [x[0] for x in tags.FREESTYLE_EVENT_LIST + tags.CHOREO_EVENT_LIST]
    print 'Content-type: text/plain\n\n'
    for event_type in event_types:
        model = 'dancedeets/training_csv-%s.txt' % event_type
        training_features = get_training_features(fb_event)
        post_dict = {'input': {'csvInstance': training_features}}
        prediction = service.predict(body=post_dict, data=model).execute()
        print event_type, prediction['outputValue']
