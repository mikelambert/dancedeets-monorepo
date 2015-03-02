#!/usr/bin/python

import multiprocessing
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

def mp_classify(arg):
    classifier, (id, fb_event) = arg
    result = classifier(fb_event)
    if result:
        return (True, id)
    else:
        return (False, id)

def init_worker():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    import os
    os.nice(5)

def mp_partition_ids(ids, classifier=lambda x:False, workers=None):
    if not workers:
        workers = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=workers, initializer=init_worker)
    print "Generating data..."
    data = [(classifier, x) for x in processing.all_fb_data(ids)]
    print "Running multiprocessing classifier..."
    async_results = pool.map_async(mp_classify, data, chunksize=100)
    # We need to specify a timeout to get(), so that KeyboardInterrupt gets delivered properly.
    results = async_results.get(9999999)
    print "Multiprocessing classifier completed."
    successes = set(x[1] for x in results if x[0])
    fails = set(x[1] for x in results if not x[0])
    return processing.ClassifiedIds(successes, fails)

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
classifier_data = mp_partition_ids(trial_ids, classifier=basic_match)
print "done, %d seconds" % (time.time() - a)

score_card = processing.ClassifierScoreCard(training_data, classifier_data, positive_classifier)

print "Found %s true-positives, %s false-positives" % (len(score_card.true_positives), len(score_card.false_positives))
print "Leaves %s to be manually-classified" % (len(score_card.false_negatives))
                
if full_run:
    score_card.write_to_disk('scratch/')

for id in score_card.false_positives:
    print 'F', id
