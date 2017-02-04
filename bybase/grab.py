#!/usr/bin/python

import datetime
import getpass
import logging
import json
import urllib2

path = '/Users/%s/Dropbox/dancedeets/private/bybase-usernamepassword.txt' % getpass.getuser()
username, password = [x.strip() for x in open(path).readlines()]
first_url = 'http://185.7.80.229/web/oauth/token/'
first_data = 'client_secret=EEEgyMhYSPbiH1daC4G4KctYE7Tlq3&client_id=7xY6XoCUj6172CLrspX5rscLkdyIXE&grant_type=password&username=%s&password=%s' % (username, password)
data = json.loads(urllib2.urlopen(first_url, first_data).read())
print data

url = 'http://185.7.80.229/web/wp-json/bybase/v1/events?page_size=10000&access_token=%s' % data['access_token']
data = urllib2.urlopen(url, timeout=30).read()
d = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
events = json.loads(data)
open('events-%s.json' % (d), 'w').write(data)

