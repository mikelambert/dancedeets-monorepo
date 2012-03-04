#!/usr/bin/python

import sys
sys.path += ['.']
import time
from logic import event_classifier
from classifiers import processing

ids_info = processing.load_ids()
for x in ids_info:
    print x, len(ids_info[x])
good_ids = ids_info['good_ids']
bad_ids = ids_info['bad_ids']
combined_ids = ids_info['combined_ids']

def handle_new_false_negative(id, ec):
    print "fn", [(k, v) for (k, v) in ec.__dict__.iteritems() if k not in ['search_text', 'times']]
def handle_new_false_positive(id, ec):
    print "fp", [(k, v) for (k, v) in ec.__dict__.iteritems() if k not in ['search_text', 'times']]


START_EVENT = 0
END_EVENT = 0
def partition_ids(old_true_positive, old_true_negative, classifier=event_classifier.ClassifiedEvent):
    success = set()
    fail = set()
    a = time.time()
    for i, (id, fb_event) in enumerate(processing.all_fb_data(combined_ids)):
        if not i % 10000: print 'Processing ', i
        if i < START_EVENT:
            continue
        if END_EVENT and i > END_EVENT:
            break
        result = classifier(fb_event)
        result.classify()
        if result.is_dance_event():
            success.add(id)
            if id in old_true_negative:
                handle_new_false_positive(result)
        else:
            # To print out failures, to see if there's any way we can better detect them
            #if id in good_ids:
            #    print id, fb_event['info'].get('name')
            #    print result.found_dance_matches, result.found_event_matches, result.found_wrong_matches
            fail.add(id)
            if id in old_true_positive:
                handle_new_false_negative(result)
    print 'Time per event: %s' % (1.0 * (time.time() - a) / (max(END_EVENT, i) - START_EVENT))
    return fail, success

# TODO(lambert): move this all into a proper main()

import sys
import getopt
opt_data = getopt.getopt(sys.argv[1:], 'o:i:')
opts = dict(opt_data[0])
if not opts.get('-i'):
    opts['-i'] = 'old_eval'


print '--- using old filter ---'
if opts.get('-i'):
    old_fail = frozenset(x.strip() for x in open(opts['-i']+".fail").readlines())
    old_succeed = frozenset(x.strip() for x in open(opts['-i']+".succeed").readlines())
old_true_positive = old_succeed.intersection(good_ids)
old_false_positive = old_succeed.intersection(bad_ids)
old_false_negative = old_fail.intersection(good_ids)
old_true_negative = old_fail.intersection(bad_ids)
print 'false negatives', len(old_false_negative)
print 'true negatives', len(old_true_negative)

print '---'
fail, succeed = partition_ids(old_true_positive, old_true_negative)
if opts.get('-o'):
    open(opts['-o']+".fail", 'w').writelines([x+"\n" for x in fail])
    open(opts['-o']+".succeed", 'w').writelines([x+"\n" for x in succeed])
true_positive = succeed.intersection(good_ids)
false_positive = succeed.intersection(bad_ids)
false_negative = fail.intersection(good_ids)
true_negative = fail.intersection(bad_ids)
print 'false negatives', len(false_negative)
print 'true negatives', len(true_negative)


print '-----'
print "Events we helped find:", len(true_positive.difference(old_true_positive))
print "Events we will miss:", len(false_negative.difference(old_false_negative))
print "Events we will waste time on:", len(false_positive.difference(old_false_positive))
print "Events we saved time on:", len(true_negative.difference(old_true_negative))

print 'list of used-to-be-positive now-negative dance events (things we will miss)'
for id in false_negative.difference(old_false_negative):
    print id
    continue
    
print ''
print ''

print 'list of used-to-be-negative now-positive non-dance events (extra useless work)'
for id in false_positive.difference(old_false_positive):
    print id

