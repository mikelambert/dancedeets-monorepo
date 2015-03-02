#!/usr/bin/python

import multiprocessing
import os
import sys
import time
sys.path += ['.']
from classifiers import processing
from nlp import event_auto_classifier
from nlp import event_classifier


all_ids = processing.load_all_ids()
classified_ids = processing.load_classified_ids(all_ids)

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
    return successes, fails

positive_classifier = True
def basic_match(fb_event):
    e = event_classifier.get_classified_event(fb_event)
    if not full_run:
        print e.processed_text.get_tokenized_text()
    if positive_classifier:
        result = event_auto_classifier.is_auto_add_event(e)
        #result = event_auto_classifier.has_good_djs_title(e)
        #result = event_auto_classifier.is_workshop(e)
    else:
        result = event_auto_classifier.is_auto_notadd_event(e)
        #result = event_auto_classifier.is_bad_classical_dance(e)
    # classified as good, but not supposed to be in the good set of ids:
    if result[0] and fb_event['info']['id'] not in good_ids:
        # false positive
        print fb_event['info']['id'], result
    if not full_run:
        print fb_event['info']['id'], result
    return result[0]

if positive_classifier:
    good_ids = classified_ids.good_ids
    bad_ids = classified_ids.bad_ids
else:
    bad_ids = classified_ids.good_ids
    good_ids = classified_ids.bad_ids

a = time.time()
print "Running auto classifier..."
theory_good_ids, theory_bad_ids = mp_partition_ids(trial_ids, classifier=basic_match)
print "done, %d seconds" % (time.time() - a)


false_positives = theory_good_ids.difference(good_ids)
false_negatives = theory_bad_ids.difference(bad_ids)
true_positives = theory_good_ids.difference(bad_ids)
true_negatives = theory_bad_ids.difference(good_ids)

print "Found %s true-positives, %s false-positives" % (len(true_positives), len(false_positives))
print "Leaves %s to be manually-classified" % (len(false_negatives))

if full_run:
    try:
        os.makedirs('scratch')
    except OSError:
        pass
    open('scratch/false_positives.txt', 'w').writelines('%s\n' % x for x in sorted(false_positives))
    open('scratch/false_negatives.txt', 'w').writelines('%s\n' % x for x in sorted(false_negatives))
    open('scratch/true_positives.txt', 'w').writelines('%s\n' % x for x in sorted(true_positives))
    open('scratch/true_negatives.txt', 'w').writelines('%s\n' % x for x in sorted(true_negatives))

for id in false_positives:
    print 'F', id
