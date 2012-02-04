#!/usr/bin/python

import csv
import json
import sys
sys.path += ['.']
from logic import event_classifier
from logic import event_classifier2

good_ids = set()
for row in csv.reader(open('local_data/DBEvent.csv')):
    good_ids.add(row[0])

potential_ids = set()
for row in csv.reader(open('local_data/PotentialEvent.csv')):
    potential_ids.add(row[0])

potential_and_good_ids = potential_ids.intersection(good_ids)
potential_and_bad_ids = potential_ids.difference(good_ids)

combined_ids = potential_ids.union(good_ids)

def all_fb_data():
    csv.field_size_limit(1000000000)
    for row in csv.reader(open('local_data/FacebookCachedObject.csv')):
        source_id, row_id, row_type = row[0].split('.')
        if source_id == "701004" and row_type == 'OBJ_EVENT' and row_id in combined_ids:
            fb_event = json.loads(row[1])
            if fb_event and not fb_event['deleted'] and fb_event['info']['privacy'] == 'OPEN':
                yield row_id, fb_event


START_EVENT = 0
END_EVENT = 0
def partition_ids(classifier=event_classifier.ClassifiedEvent):
    success = set()
    fail = set()
    for i, (id, fb_event) in enumerate(all_fb_data()):
        if not i % 10000: print 'Processing ', i
        if i < START_EVENT:
            continue
        if END_EVENT and i > END_EVENT:
            break
        result = classifier(fb_event)
        result.classify()
        if result.is_dance_event():
            success.add(id)
        else:
            # To print out failures, to see if there's any way we can better detect them
            #if id in good_ids:
            #    print id, fb_event['info'].get('name')
            #    print result.found_dance_matches, result.found_event_matches, result.found_wrong_matches
            fail.add(id)
    return fail, success

print 'good', len(good_ids)
print 'potential', len(potential_ids)
print 'potential-and-good', len(potential_and_good_ids)
print 'potential-and-bad', len(potential_and_bad_ids)


print '---'
fail, succeed = partition_ids()
false_negative = fail.difference(potential_and_bad_ids)
true_negative = fail.intersection(potential_and_bad_ids)
print 'false negatives', len(false_negative)
print 'true negatives', len(true_negative)

print '--- using old filter ---'
fail2, succeed2 = partition_ids(classifier=event_classifier2.ClassifiedEvent)
false_negative2 = fail2.difference(potential_and_bad_ids)
true_negative2 = fail2.intersection(potential_and_bad_ids)
print 'false negatives', len(false_negative2)
print 'true negatives', len(true_negative2)

print 'list of used-to-be-positive now-negative dance events'
for id in false_negative.difference(false_negative2):
    print id
    continue
    fb_event = get_fb_event(id)
    print 'F', id, fb_event['info'].get('owner', {}).get('name'), fb_event['info']['name']
    old = event_classifier.ClassifiedEvent(fb_event).is_dance_event()
    new = event_classifier2.ClassifiedEvent(fb_event).is_dance_event()
    print '  ', old, new

print ''
print ''

print 'list of used-to-be-negative now-positive non-dance events'
for id in true_negative2.difference(true_negative):
    print id
    continue
    fb_event = get_fb_event(id)
    print 'F', id, fb_event['info'].get('owner', {}).get('name'), fb_event['info']['name']
    old = event_classifier.ClassifiedEvent(fb_event).is_dance_event()
    new = event_classifier2.ClassifiedEvent(fb_event).is_dance_event()
    print '  ', old, new

