import json
import logging
import requests

from dancedeets.util import urls

API_KEY = 'AIzaSyAMTDdM6Y8xDkS7zaj3nRWmxK01rHznlB0'

MAX_LENGTH = 5000


def check_language(text):
    if len(text) > MAX_LENGTH:
        logging.info("trimming text from %s to %s", len(text), MAX_LENGTH)
        text = text[:MAX_LENGTH]
    base_url = 'https://www.googleapis.com/language/translate/v2/detect'
    params = {'key': API_KEY, 'q': text}
    form_data = urls.urlencode(params)
    # Use requests library for HTTP calls
    result = requests.post(base_url, data=form_data, headers={'X-HTTP-Method-Override': 'GET'}, timeout=20)
    if result.status_code != 200:
        error = "result status code is %s for content %s" % (result.status_code, result.text)
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
