#!/usr/bin/python

import sys
import time
sys.path += ['.']
from classifiers import processing
from nlp import categories


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
    styles = categories.find_styles(fb_event)
    if not full_run:
        # debug
        print fb_event['info'].get('name', '').encode('utf-8')
        print fb_event['info'].get('description', '').encode('utf-8')

    if 'LOCK' in styles:
        print fb_event['info']['id']
        #contexts = categories.get_context(fb_event, styles['LOCK'])
        #for keyword, context in zip(styles['LOCK'], contexts):
        #    print keyword, repr(context)

    return 'LOCK' in styles

a = time.time()
print "Running auto classifier..."
fb_data = processing.all_fb_data(trial_ids)
# Input fb_data is [(id, fb_event), (id, fb_event)]
# Result will be positive ids and negative ids
classifier_data = processing.partition_data(fb_data, classifier=basic_match)
print "done, %d seconds" % (time.time() - a)

score_card = processing.ClassifierScoreCard(training_data, classifier_data, positive_classifier)

print "Found %s true-positives, %s false-positives" % (len(score_card.true_positives), len(score_card.false_positives))
print "Leaves %s to be manually-classified" % (len(score_card.false_negatives))
                
if full_run:
    score_card.write_to_disk('scratch/')

for id in score_card.false_positives:
    print 'F', id
