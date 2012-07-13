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


ids_info = processing.load_ids()
for x in ids_info:
        print x, len(ids_info[x])
classified_ids = ids_info['good_ids']
all_ids = ids_info['combined_ids']

def partition_ids(ids, classifier=lambda x:False):
    successes = set()
    fails = set()
        for i, (id, fb_event) in enumerate(processing.all_fb_data(ids)):
        if not i % 10000: print 'Processing ', i
        result = classifier(fb_event)
        if result:
            successes.add(id)
        else:
            fails.add(id)
    return successes, fails

positive_classifier = False
def basic_match(fb_event):
    e = event_classifier.get_classified_event(fb_event)
    if positive_classifier:
        result = event_auto_classifier.is_auto_add_event(e)
    else:
        result = event_auto_classifier.is_auto_notadd_event(e)
    if result[0] and fb_event['info']['id'] not in good_ids:
        print fb_event['info']['id'], result
    return result[0]

if positive_classifier:
    good_ids = classified_ids
    bad_ids = all_ids.difference(good_ids)
else:
    bad_ids = classified_ids
    good_ids = all_ids.difference(bad_ids)

a = time.time()
print "Running auto classifier..."
theory_good_ids, theory_bad_ids = partition_ids(all_ids, classifier=basic_match)
print "done, %d seconds" % (time.time() - a)


false_positives = theory_good_ids.difference(good_ids)
false_negatives = theory_bad_ids.difference(bad_ids)
true_positives = theory_good_ids.difference(bad_ids)
true_negatives = theory_bad_ids.difference(good_ids)

#open('scratch/false_positives.txt', 'w').writelines('%s\n' % x for x in false_positives)
#open('scratch/false_negatives.txt', 'w').writelines('%s\n' % x for x in false_negatives)
#open('scratch/true_positives.txt', 'w').writelines('%s\n' % x for x in true_positives)
#open('scratch/true_negatives.txt', 'w').writelines('%s\n' % x for x in true_negatives)

print "Found %s true-positives, %s false-positives" % (len(true_positives), len(false_positives))
print "Leaves %s to be manually-classified" % (len(false_negatives))

for id in false_positives:
        print 'F', id
