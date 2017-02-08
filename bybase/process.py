#!/usr/bin/python

import datetime
import getpass
import glob
import logging
import HTMLParser
import json
import os
import sys
import time
import urllib
import urllib2

# PROCESSING: 353672721655806 killason ...and afterwards

logging.getLogger().setLevel(logging.INFO)

path = '/Users/%s/Dropbox/dancedeets/private/fb-token.txt' % getpass.getuser()
fb_access_token = open(path).read().strip()

recent = sorted(glob.glob('events-*.json'))[-1]
data = open(recent).read()
eventData = json.loads(data)
count = len(eventData)
txt = open('eventList-%s.txt' % (count), 'w')

def exists(e):
    cache_filename = 'dd_cached/%s.txt' % e['id']
    if os.path.exists(cache_filename):
        data = open(cache_filename).read()
        response = json.loads(data)
    else:
        logging.info('Searching for event %s in DanceDeets', e['id'])
        title = e['title'].replace('+', '')
        title = HTMLParser.HTMLParser().unescape(title)
        qs = urllib.urlencode({
            'location': '',
            'time_period': 'UPCOMING',
            'keywords': title.encode('utf-8'),
            'client': 'cmdline',
        })
        url = 'http://www.dancedeets.com/api/v1.3/search?%s' % qs
        data = urllib2.urlopen(url, '{"client": "cmdline"}', timeout=3).read()
        response = json.loads(data)
        if not 'results' in response:
            logging.error(url)
            logging.error(response)
        else:
            open(cache_filename, 'w').write(data)
    if 'results' in response:
        if response['results']:
            return True

    # Just in case, search FB and see if the ID we get is on dancedeets
    found_events = find_fb_ids(e)
    for fb_event in found_events:
        if dd_id_exists(fb_event['id']):
            return True

    return False

def dd_id_exists(eid):
    cache_filename = 'dd_id_cached/%s.txt' % eid
    if os.path.exists(cache_filename):
        data = open(cache_filename).read()
        response = json.loads(data)
    else:
        logging.info('Looking up info for event %s in DanceDeets', eid)
        url = 'http://www.dancedeets.com/api/v1.3/events/%s' % eid
        data = urllib2.urlopen(url, timeout=2).read()
        response = json.loads(data)
        open(cache_filename, 'w').write(data)
    if 'id' in response:
        return True
    else:
        return False


def write_line(fields):
    txt.write('\t'.join(fields).encode('utf-8'))
    txt.write('\n')


def find_fb_ids(e):
    cache_filename = 'fb_cached/%s.txt' % e['id']
    title = HTMLParser.HTMLParser().unescape(e['title'])
    fb_results = None
    if os.path.exists(cache_filename):
        data = open(cache_filename).read()
        fb_results = json.loads(data)
        if 'error' in fb_results:
            fb_results = None
    if not fb_results:
        access_token = fb_access_token
        logging.info('Searching for event id %s on FB', e['id'])
        fb_search_url = 'https://graph.facebook.com/v2.8/search?type=event&q=%s&access_token=%s' % (urllib.quote(title.encode('utf-8')), access_token)
        data = urllib2.urlopen(fb_search_url, timeout=2).read()
        fb_results = json.loads(data)
        if 'error' in fb_results:
            logging.error('Error loading FB search: %s', fb_results['error'])
        else:
            open(cache_filename, 'w').write(data)
        time.sleep(2)
    if 'data' in fb_results:
        found_results = fb_results['data']
        found_events = [event for event in found_results if event['name'] == title]
        return found_events
    else:
        return []

def print_find_status(e, found_events):
    title = HTMLParser.HTMLParser().unescape(e['title'])
    for fb_event in found_events:
        found = dd_id_exists(fb_event['id'])
        if found:
            print 'JUST KIDDING: We have this: ', title.encode('utf-8')
            return
    if len(found_events) == 0:
        print 'Event', e['id'], 'not found:', title.encode('utf-8')
    elif len(found_events) == 1:
        fb_event = found_events[0]
        print 'Found', fb_event['id'], fb_event['name'].encode('utf-8')
    else:
        print 'Found too many events:'
        for fb_event in found_events:
            print 'Possibly', fb_event['name'].encode('utf-8'), fb_event['id']


header = ['DD Knew?', 'From FB?', 'Add Date', 'Start Date', 'id', 'Type', 'Style', 'Title']
write_line(header)
for e in eventData:
    fb = 'FB_IMG' if 'fbcdn' in e['headline_picture_link'] else 'NOT_FB'
    fields = [
        'DDE' if exists(e) else 'NEW',
        fb,
        e['post_date_utc'],
        e['date'],
        e['id'],
        ', '.join(e['type']),
        ', '.join(e['style']),
        e['title'],
    ]
    fields = [x.replace('\t', ' ') for x in fields]
    write_line(fields)

posts = {}
events = {}

for e in eventData:
    post_date = e['post_date_utc'][:10]
    posts.setdefault(post_date, []).append(e)

    event_date = e['date'][:10]
    events.setdefault(event_date, []).append(e)

future = {}
status = {}
countries = {}
new_countries = {}

now = datetime.datetime.now().strftime('%Y-%m-%D %H:%M:%S')
print 'Missing:'
for e in eventData:
    if e['date'] < now:
        continue
    future[e['id']] = True
    e_exists = exists(e)
    status[e['id']] = e_exists
    countries.setdefault(e['state'], []).append(e)
    if not e_exists:
        new_countries.setdefault(e['state'], []).append(e)
    
print 'Post-Ups:'
for post_date, lst in sorted(posts.items()):
    print post_date, len(lst)
    for e in lst:
        ids = [x['id'] for x in find_fb_ids(e)]
        print '  ', 'X' if status[e['id']] else '-', ids, e['title']

#print 'Events:'
#for post_date, count in sorted(events.items()):
#    print post_date, count

print 'Countries:'
for country, lst in sorted(countries.items(), key=lambda x: len(x[1]))[-10:]:
    print country, len(lst)

print 'New Countries:'
for country, lst in sorted(new_countries.items(), key=lambda x: len(x[1]))[-10:]:
    print country, len(lst)
    for e in lst:
        ids = [x['id'] for x in find_fb_ids(e)] if not status[e['id']] else '--'
        print '  ', 'X' if status[e['id']] else '-', ids, e['title']

print 'Coverage:'
existIds = [x for x in status if status[x]]
print '%.02f' % (1.0 * len(existIds) / len(future))


for e in eventData:
    if future.get(e['id']) and not status[e['id']]:
        found_events = find_fb_ids(e)
        print_find_status(e, found_events)

