#!/usr/bin/python

import datetime
import getpass
import logging
import json
import urllib
import urllib2

path = '/Users/%s/Dropbox/dancedeets/private/bybase-usernamepassword.txt' % getpass.getuser()
username, password = [x.strip() for x in open(path).readlines()]
first_url = 'http://185.7.80.229/web/oauth/token/'
first_data = 'client_secret=EEEgyMhYSPbiH1daC4G4KctYE7Tlq3&client_id=7xY6XoCUj6172CLrspX5rscLkdyIXE&grant_type=password&username=%s&password=%s' % (username, password)
data = json.loads(urllib2.urlopen(first_url, first_data).read())
print data

all_events = []
last_id = None
page_size = 1000
while True:
    args = {
        'page_size': page_size,
        'access_token': data['access_token'],
    }
    if last_id:
        args['after_id'] = last_id
    url = 'http://185.7.80.229/web/wp-json/bybase/v1/events?%s' % urllib.urlencode(args)
    print url
    try:
        event_data = urllib2.urlopen(url, timeout=60).read()
    except urllib2.HTTPError as e:
        print 'Got Error:', e
        page_size = page_size / 3
        if page_size == 0:
            break
        continue
    events = json.loads(event_data)
    if not events:
        break
    last_id = events[-1]['id']
    all_events.extend(events)

d = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
open('events-%s.json' % (d), 'w').write(json.dumps(all_events))

