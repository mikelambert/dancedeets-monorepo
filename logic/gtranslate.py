import logging
import urllib

try:
    import json
except ImportError:
    from django.utils import simplejson as json

urllib2_fallback = False
try:
    from google.appengine.api import urlfetch
except ImportError:
    urllib2_fallback = True
    import urllib2

API_KEY = 'AIzaSyAMTDdM6Y8xDkS7zaj3nRWmxK01rHznlB0'

MAX_LENGTH = 5000
def check_language(text):
    if len(text) > MAX_LENGTH:
        logging.info("trimming text from %s to %s", len(text), MAX_LENGTH)
        text = text[:MAX_LENGTH]
    base_url = 'https://www.googleapis.com/language/translate/v2/detect'
    params = {'key': API_KEY, 'q': text.encode('utf8')}
    form_data = urllib.urlencode(params)
    if urllib2_fallback:
        request = urllib2.Request(base_url, form_data, {'X-HTTP-Method-Override': 'GET'})
        response_content = urllib2.urlopen(request).read()
    else:
        result = urlfetch.fetch(url=base_url,
            payload=form_data,
            method=urlfetch.POST,
            headers={'X-HTTP-Method-Override': 'GET'})
        if result.status_code != 200:
            error = "result status code is %s for content %s" % (result.status_code, result.content)
            logging.error(error)
            raise Exception("Error in translation: %s" % error)
        response_content = result.content
    json_content = json.loads(response_content)
    real_results = json_content['data']['detections'][0][0]
    logging.info("text classification returned %s", real_results)
    if real_results['confidence'] > 0.10:
        return real_results['language']
    else:
        return None


