#!/usr/bin/python

import sys
import time
sys.path += ['.']
from classifiers import processing
from nlp import event_auto_classifier
from nlp import event_classifier


all_ids = processing.load_all_ids()
training_data = processing.load_classified_ids(all_ids)

if len(sys.argv) > 1:
    full_run = False
    trial_ids = set(sys.argv[1:])
else:
    full_run = True
    trial_ids = all_ids


positive_classifier = True
def basic_match(fb_event):
    e = event_classifier.get_classified_event(fb_event)
    if not full_run:
        print e.processed_text.get_tokenized_text()
    if positive_classifier:
        result = event_auto_classifier.is_auto_add_event(e)
    else:
        result = event_auto_classifier.is_auto_notadd_event(e)
    # classified as good, but not supposed to be in the good set of ids:
    if result[0] and fb_event['info']['id'] not in training_data.good_ids:
        # false positive
        print fb_event['info']['id'], result
    if not full_run:
        print fb_event['info']['id'], result
    return result[0]

a = time.time()
print "Running auto classifier..."
fb_data = processing.all_fb_data(trial_ids)
# Input fb_data is [(id, fb_event), (id, fb_event)]
# Result will be positive ids and negative ids
classifier_data = processing.Classifier.partition_data(fb_data, classifier=basic_match)
print "done, %d seconds" % (time.time() - a)

score_card = processing.ClassifierScoreCard(training_data, classifier_data, positive_classifier)

print "Found %s true-positives, %s false-positives" % (len(score_card.true_positives), len(score_card.false_positives))
print "Leaves %s to be manually-classified" % (len(score_card.false_negatives))
                
if full_run:
    score_card.write_to_disk('scratch/')

for id in score_card.false_positives:
    print 'F', id
