#!/usr/bin/python

import csv
import json
import re
import sys
import time
sys.path += ['.']
from logic import event_classifier

#set to True if we want to find things to "yes this is good event"
#set to False to find-and-trim out things for "no this is definitely not event"
positive_classifier = False

a = time.time()
print "Loading fb data..."
fb_entries = {}
csv.field_size_limit(1000000000)
found_event_ids = set()
for i, row in enumerate(csv.reader(open('local_data/FacebookCachedObject.csv'))):
    if i % 10000 == 0:
        print 'Loading fb row %s' % i
    #if i > 20000:
    #    break
    source_id, row_id, row_type = row[0].split('.')
    if source_id == "701004" and row_type == "OBJ_EVENT":
        fb_entries[row[0]] = json.loads(row[1])
        found_event_ids.add(row_id)
print "done, %d seconds, using %s events" % ((time.time() - a), len(found_event_ids))

_bad_ids = """262185997192054
262185997192054
189005731208734
252332548180183
169340009836878
210695735694992
315317571849986
345028368870869
135376583251341
190975384341716
149359838517414
262466083828178
334260309950061
275111512554233
302921526433940
210695735694992
253269711419677
208443532587437
358004127561923
369091239773418
244492588972542
113424452119494
359814084043065
330235107008484
345691242131785
331342693571264
361972543821487
378619662155354
296801027050137
305099059548738
253268444751346
162154073886560
290835774303963
358864257465796
343414719013429
185045374930911
246115828796607
292703670784103
227695903989563
351924681488160
253704941372041
215477448534686
180738645369143""".split("\n")

_good_ids = """236467306447169
195475827220494
294273573970277
348784985154156
385669834783774
250371245042502
157335347716233
387123937980600
318299674872576
225370597555828
344311292276178""".split("\n")

classified_ids = {}
for row in csv.reader(open('local_data/DBEvent.csv')):
    # Let's us work on the subset of the data:
    if row[0] in found_event_ids:
        classified_ids[row[0]] = row[2].split(';')

potential_ids = set()
for row in csv.reader(open('local_data/PotentialEvent.csv')):
    # Let's us work on the subset of the data:
    if row[0] in found_event_ids:
        potential_ids.add(row[0])

all_ids = potential_ids.union(classified_ids)

def get_fb_event(id):
    EVENT_KEY = '701004.%s.OBJ_EVENT'
    key = EVENT_KEY % id
    if key not in fb_entries:
        return None
    fb_event = fb_entries[key]
    if fb_event['deleted']:
        return None
    return fb_event

def partition_ids(ids, classifier=lambda x:False):
    successes = set()
    fails = set()
    for id in ids:
        fb_event = get_fb_event(id)
        if not fb_event: continue
        result = classifier(fb_event)
        if result:
            successes.add(id)
        else:
            fails.add(id)
    return successes, fails

def get_stripped(fb_id, stripper):
    fb_event = get_fb_event(fb_id)
    if fb_event:
        search_text = (fb_event['info'].get('name', '') + ' ' + fb_event['info'].get('description', '')).lower()
    else:
        search_text = ''
    search_text = stripper(search_text)
    return search_text

def split_words_for_id(id, stripper):
    search_text = get_stripped(id, stripper)
    words = re.split(r'\s+', search_text)
    if 1:
        return frozenset(words)
    else:
        return frozenset(['%s %s' % (words[i], words[i+1]) for i in range(len(words)-1)])

def get_keyword_mapping(all_ids, stripper=lambda x:x):
    keyword_mapping = {}
    for fb_id in all_ids:
        search_text = get_stripped(fb_id, stripper)
        #TODO(lambert): also explore bigrams
        keyword_mapping[fb_id] = split_words_for_id(fb_id, stripper)        
    return keyword_mapping

def get_df(ids, stripper=lambda x:x):
    words = {}
    for id in ids:
        for word in split_words_for_id(id, stripper):
            words[word] = words.get(word, 0) + 1
    words_df = dict((x[0], 1.0*x[1]/len(ids)) for x in words.items())
    return words_df

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



basic_keywords = ['judges', 'locking', 'bboy', 'popping', 'waacking', 'bboying', 'krump']
basic_keywords += ['lockin', 'bgirl', 'boogiezone', 'newstyle', 'cyphers']
basic_keywords += ['dance battle', 'battles start']
basic_keywords += ['1[\s-]*(?:vs?.?|on)[\s-]*1', '2[\s-]*(?:vs?.?|on)[\s-]*2',  '3[\s-]*(?:vs?.?|on)[\s-]*3', '5[\s-]*(?:vs?.?|on)[\s-]*5', '4[\s-]*(?:vs?.?|on)[\s-]*4']

if positive_classifier:
    basic_neg_keywords = ['party', 'dj', 'night']
    basic_neg_keywords += ['streetball', 'guitar', 'act', 'rap', 'vote', 'bottle', 'film', 'talent', 'fundraiser', 'shoot', 'graffiti', 'scratch', 'casting', 'votes', 'donate', 'singer', 'sing', 'support', 'booty', 'costume', 'boba', 'bobas', 'yoga']
    # popping bobas
    # support XX
    # booty ...battle/contest/judges
    # custome contest
    basic_neg_keywords += ['contemporary']
else:
    basic_keywords = ['edm', 'dub,', 'imprint', 'selectors', 'dnb', 'headliners', 'karaoke']
    basic_neg_keywords = ['dance', 'dancers']

basic_keywords = []
basic_neg_keywords = []

# for battle/competition classifier
#basic_keywords = 'judges', '1[\s-]*(?:vs?.?|on)[\s-]*1', '2[\s-]*(?:vs?.?|on)[\s-]*2',  '3[\s-]*(?:vs?.?|on)[\s-]*3', '5[\s-]*(?:vs?.?|on)[\s-]*5', '4[\s-]*(?:vs?.?|on)[\s-]*4', 'prelims', 'preselections', 'top 16', 'top 8', 'to smoke']
# basic_neg_keywords = ['the judges', 'dance', 'hip', 'night', 'people', 'open mic', 'games?', '2006', 'battle of']

if basic_keywords:
    basic_re = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(basic_keywords))
else:
    basic_re = re.compile(r'XXXCSDCWEFWEF')
if basic_neg_keywords:
    basic_neg_re = re.compile(r'(?i)\b(?:%s)\b' % '|'.join(basic_neg_keywords))
else:
    basic_neg_re = re.compile(r'XXXCSDCWEFWEF')

def basic_match(fb_event):
    search_text = (fb_event['info'].get('name', '') + ' ' + fb_event['info'].get('description', '')).lower()
    if basic_neg_keywords and basic_neg_re.search(search_text):
        return False
    return basic_re.search(search_text)

def strip_basic_all(text):
    return basic_neg_re.sub('', basic_re.sub('', text))
def strip_basic_neg(text):
    return basic_neg_re.sub('', text)

def get_matches(fb_event):
    search_text = (fb_event['info'].get('name', '') + ' ' + fb_event['info'].get('description', '')).lower()
    return basic_re.findall(search_text), basic_neg_re.findall(search_text)

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

open('scratch/false_positives.txt', 'w').writelines('%s\n' % x for x in false_positives)
open('scratch/false_negatives.txt', 'w').writelines('%s\n' % x for x in false_negatives)
open('scratch/true_positives.txt', 'w').writelines('%s\n' % x for x in true_positives)
open('scratch/true_negatives.txt', 'w').writelines('%s\n' % x for x in true_negatives)

print "Found %s true-positives, %s false-positives" % (len(true_positives), len(false_positives))
print "Leaves %s to be manually-classified" % (len(false_negatives))

debug_bad_keywords = False
if debug_bad_keywords:
    for kw in basic_neg_keywords:
        kw_re = re.compile(r'(?i)\b(?:%s)\b' % kw)
        def kw_match(fb_event):
            search_text = (fb_event['info'].get('name', '') + ' ' + fb_event['info'].get('description', '')).lower()
            return kw_re.search(search_text)

        good_excluded, good_ignored = partition_ids(good_ids, classifier=kw_match)
        bad_excluded, bad_ignored = partition_ids(bad_ids, classifier=kw_match)
        print "Keyword %r excludes %s good, %s bad events" % (kw, len(good_excluded), len(bad_excluded))

for id in false_positives:
        fb_event = get_fb_event(id)
        print 'F', id, get_matches(fb_event)

print "Computing DFs..."
df_false_negatives = get_df(false_negatives, stripper=strip_basic_all)
df_bad_ids = get_df(bad_ids, stripper=strip_basic_all)
print "Best Positive Words:"
print_top_for_df(df_minus_df(df_false_negatives, df_bad_ids, negative_scale=10))

print "Computing DFs..."
df_false_positives = get_df(false_positives, stripper=strip_basic_neg)
df_good_ids = get_df(good_ids, stripper=strip_basic_neg)
print "Best Negative Words:"
print_top_for_df(df_minus_df(df_false_positives, df_good_ids, negative_scale=1.0))

import sys
sys.exit()



for success_type, success_ids in successes.iteritems():
    true_positives = success_ids.intersection(good_ids)
    false_positives = success_ids.difference(good_ids)
    true_list_dict = get_df(true_positives)
    false_list_dict = get_df(false_positives)

    diff_list = sorted_df(df_minus_df(true_list_dict, false_list_dict))
    negative_keywords = [x[0] for x in diff_list[:20]]
    positive_keywords = [x[0] for x in diff_list[-50:]]

    print ''
    print success_type, "Negative:"
    print '\n'.join(negative_keywords)
    print ''
    print success_type, "Positive:"
    print '\n'.join(positive_keywords)
    print ''

print 'good', len(good_ids)
print 'potential', len(potential_ids)
print 'potential-and-good', len(potential_and_good_ids)
print 'potential-and-bad', len(potential_and_bad_ids)

