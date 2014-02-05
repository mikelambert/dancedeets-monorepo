#!/usr/bin/python

import sys
import time
sys.path += ['.']
from logic import event_auto_classifier
from logic import event_classifier
from classifiers import processing

positive_classifier = True

def success(ce, fb_event, result):
    pass
    #print fb_event['info']['id'], fb_event['info'].get('name').encode('utf-8')

def failure(ce, fb_event, result):
    if event_classifier.all_regexes['battle_regex'][ce.boundaries].search(ce.search_text):
        print fb_event['info']['id'], fb_event['info'].get('name').encode('utf-8'), result

def partition_ids():
    for i, (id, fb_event) in enumerate(processing.all_fb_data([], filename='local_data/PotentialFBEvents.csv')):
        e = event_classifier.get_classified_event(fb_event)
        result = event_auto_classifier.is_battle(e)
        if result[0]:
            success(e, fb_event, result)
        else:
            failure(e, fb_event, result)

a = time.time()
print "Running auto classifier..."
partition_ids()
print "done, %d seconds" % (time.time() - a)

