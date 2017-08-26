#!/usr/bin/python

import logging
import json
import urllib2

URLS = [
    'https://www.dancedeets.com/login?next=%2F%3F',
    'https://www.dancedeets.com/?location=USA',
    'https://www.dancedeets.com/?location=Europe',
    'https://www.dancedeets.com/?location=Asia',
    'https://www.dancedeets.com/events/386287078085795/',  # no amp page
    'https://www.dancedeets.com/events/1171204409564075/',
    'https://www.dancedeets.com/events/1171204409564075/?amp=1',
    'https://www.dancedeets.com/events/dance-delight:20554/',
    'https://www.dancedeets.com/events/dance-delight:20554/?amp=1',
    'https://www.dancedeets.com/events/street-dance-korea:190/',
    'https://www.dancedeets.com/events/street-dance-korea:190/?amp=1',
    'https://www.dancedeets.com/events/image_proxy/dance-delight:20554/',
    'https://www.dancedeets.com/events/image_proxy/1459851027584883',
    'https://www.dancedeets.com/events/image_proxy/1459851027584883/',
    'https://www.dancedeets.com/events/250492048363697/',
    'https://www.dancedeets.com/events/421615758038730',
    'https://www.dancedeets.com/events/246367547151/',  # no venue
    'https://www.dancedeets.com/events/412709132257891/',  # no description
    'https://www.dancedeets.com/events/106615749421406/',  # no location
]
API_URLS = [
    'https://www.dancedeets.com/api/v1.2/search?location=USA&time_period=UPCOMING',
    'https://www.dancedeets.com/api/v1.2/search?location=Europe&time_period=UPCOMING',
    'https://www.dancedeets.com/api/v1.2/search?location=Asia&time_period=UPCOMING',
    'https://www.dancedeets.com/api/v1.2/events/1171204409564075',
    'https://www.dancedeets.com/api/v1.2/events/dance-delight:20554',
    'https://www.dancedeets.com/api/v1.2/events/street-dance-korea:178',
]


def fetch(url):
    print url
    req = urllib2.Request(url.encode('utf-8'))
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        return e
    return response


def error(url, error):
    logging.error('URL Error: %s', url)
    logging.error('  %s', error)


for url in URLS:
    response = fetch(url)
    if isinstance(response, Exception):
        error(url, response)
    elif response.code != 200:
        error(url, response.read())

for url in API_URLS:
    response = fetch(url)
    if isinstance(response, Exception):
        error(url, response)
    else:
        data = json.loads(response.read())
        if 'errors' in data:
            error(url, data['errors'])
