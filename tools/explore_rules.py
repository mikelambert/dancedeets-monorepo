#!/usr/bin/python

import csv
import json
import sys
sys.path += ['.']
from logic import event_classifier
from logic import event_classifier2

good_ids = set()
for row in csv.reader(open('local_data/events.csv')):
    good_ids.add(row[0])

potential_ids = set()
for row in csv.reader(open('local_data/potentialevents.csv')):
    potential_ids.add(row[0])

potential_and_good_ids = potential_ids.intersection(good_ids)
potential_and_bad_ids = potential_ids.difference(good_ids)

print "Loading fb data"
fb_entries = {}
csv.field_size_limit(1000000000)
for row in csv.reader(open('local_data/fb_data.csv')):
    fb_entries[row[0]] = row[1]
print "...done"

def get_fb_event(id):
    EVENT_KEY = '701004.%s.OBJ_EVENT'
    key = EVENT_KEY % id
    if key not in fb_entries:
        return None
    fb_event = json.loads(fb_entries[key])
    if fb_event['deleted']:
        return None
    return fb_event

def partition_ids(ids, classifier=event_classifier.is_dance_event):
    success = set()
    fail = set()
    for id in ids:
        fb_event = get_fb_event(id)
        if not fb_event: continue
        result = classifier(fb_event)
        if result and result[0] != False:
            success.add(id)
        else:
            fail.add(id)
    return fail, success

print 'good', len(good_ids)
print 'potential', len(potential_ids)
print 'potential-and-good', len(potential_and_good_ids)
print 'potential-and-bad', len(potential_and_bad_ids)


print '---'
fail, succeed = partition_ids(potential_ids)
false_negative = fail.difference(potential_and_bad_ids)
true_negative = fail.intersection(potential_and_bad_ids)
print 'false negatives', len(false_negative)
print 'true negatives', len(true_negative)

print '--- using new filter ---'
fail2, succeed2 = partition_ids(potential_ids, classifier=event_classifier2.is_dance_event)
false_negative2 = fail2.difference(potential_and_bad_ids)
true_negative2 = fail2.intersection(potential_and_bad_ids)
print 'false negatives', len(false_negative2)
print 'true negatives', len(true_negative2)

print 'list of used-to-be-positive now-negative dance events'
for id in false_negative2.difference(false_negative):
    fb_event = get_fb_event(id)
    print 'F', id, fb_event['info'].get('owner', {}).get('name'), fb_event['info']['name']
    print '  ', event_classifier.is_dance_event(fb_event), event_classifier2.is_dance_event(fb_event)

print 'list of used-to-be-negative now-positive non-dance events'
for id in true_negative.difference(true_negative2):
    fb_event = get_fb_event(id)
    print 'F', id, fb_event['info'].get('owner', {}).get('name'), fb_event['info']['name']
    print '  ', event_classifier.is_dance_event(fb_event), event_classifier2.is_dance_event(fb_event)

