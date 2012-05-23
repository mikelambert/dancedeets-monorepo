#!/usr/bin/python

import csv
import json
import re
import sys
import time
sys.path += ['.']
from logic import event_auto_classifier
from logic import event_classifier
from classifiers import processing

positive_classifier = True

def success(ce, fb_event):
    pass
    #print fb_event['info']['id'], fb_event['info'].get('name').encode('utf-8')

def failure(ce, fb_event):
    if event_classifier.all_regexes['start_judge_keywords_regex'][ce.boundaries].search(ce.search_text):
        pass#print fb_event['info']['id'], fb_event['info'].get('name').encode('utf-8')

def partition_ids():
    successes = set()
    fails = set()
        for i, (id, fb_event) in enumerate(processing.all_fb_data([], filename='local_data/PotentialFBEvents.csv')):
        e = event_classifier.get_classified_event(fb_event)
        result = event_auto_classifier.is_battle(e)[0]
        if result:
            success(e, fb_event)
        else:
            failure(e, fb_event)

a = time.time()
print "Running auto classifier..."
partition_ids()
print "done, %d seconds" % (time.time() - a)

