#!/usr/bin/python

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
if len(sys.argv) > 1:
    all_ids = set([sys.argv[1]])
else:
    all_ids = ids_info['combined_ids']

TOTAL = None # magic key
def add_counts(base_counts, fb_event):
    if not keyword_counts:
        return
    search_text = event_classifier.get_relevant_text(fb_event)
    words = re.split(r'\s+', search_text)
    if 1:
        unique_words = frozenset(words)
    else:
        unique_words = frozenset(['%s %s' % (words[i], words[i+1]) for i in range(len(words)-1)])
    for word in unique_words:
        base_counts[word] = base_counts.get(word, 0) + 1
    base_counts[TOTAL] = base_counts.get(TOTAL, 0) + 1

def get_df_from_counts(counts):
    return dict((x[0], 1.0*x[1]/counts[TOTAL]) for x in counts.items())

def df_minus_df(df1, df2, negative_scale=1.0):
    all_keys = set(df1).union(df2)
    diff = {}
    for key in all_keys:
        diff[key] = df1.get(key, 0) - df2.get(key, 0) * negative_scale
    return diff

def sorted_df(df):
    diff_list = sorted(df.items(), key=lambda x: -x[1])
    return diff_list

def print_top_for_df(df):
    print '\n'.join(['%s: %s' % x for x in sorted_df(df)][:20])

def partition_ids(ids, classifier=lambda x:False):
    successes = set()
    fails = set()
    for i, (id, fb_event) in enumerate(processing.all_fb_data(ids)):
        if not i % 10000: print 'Processing ', i
        result = classifier(fb_event)
        if result:
            successes.add(id)
            if id not in good_ids:
                # false positive
                add_counts(false_positive_counts, fb_event)
        else:
            fails.add(id)
            if id not in bad_ids:
                # false negative
                add_counts(false_negative_counts, fb_event)
        if id in good_ids:
            add_counts(good_counts, fb_event)
        else:
            add_counts(bad_counts, fb_event)
    return successes, fails

positive_classifier = True
def basic_match(fb_event):
    e = event_classifier.get_classified_event(fb_event)
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
    return result[0]

if positive_classifier:
    good_ids = classified_ids
    bad_ids = all_ids.difference(good_ids)
else:
    bad_ids = classified_ids
    good_ids = all_ids.difference(bad_ids)

keyword_counts = False
good_counts = {}
bad_counts = {}
false_positive_counts = {}
false_negative_counts = {}

a = time.time()
print "Running auto classifier..."
theory_good_ids, theory_bad_ids = partition_ids(all_ids, classifier=basic_match)
print "done, %d seconds" % (time.time() - a)


false_positives = theory_good_ids.difference(good_ids)
false_negatives = theory_bad_ids.difference(bad_ids)
true_positives = theory_good_ids.difference(bad_ids)
true_negatives = theory_bad_ids.difference(good_ids)

open('scratch/false_positives.txt', 'w').writelines('%s\n' % x for x in sorted(false_positives))
open('scratch/false_negatives.txt', 'w').writelines('%s\n' % x for x in sorted(false_negatives))
open('scratch/true_positives.txt', 'w').writelines('%s\n' % x for x in sorted(true_positives))
open('scratch/true_negatives.txt', 'w').writelines('%s\n' % x for x in sorted(true_negatives))

print "Found %s true-positives, %s false-positives" % (len(true_positives), len(false_positives))
print "Leaves %s to be manually-classified" % (len(false_negatives))

if keyword_counts:
    print "Best finds for false-negatives:"
    print_top_for_df(df_minus_df(get_df_from_counts(false_negative_counts), get_df_from_counts(bad_counts), negative_scale=100))
    print "Best fixes for false-positives:"
    print_top_for_df(df_minus_df(get_df_from_counts(false_positive_counts), get_df_from_counts(good_counts), negative_scale=0.1))


for id in false_positives:
    print 'F', id
