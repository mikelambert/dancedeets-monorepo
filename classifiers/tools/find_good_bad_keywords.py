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
positive_classifier = True

classified_ids = {}
for row in csv.reader(open('local_data/DBEvent.csv')):
    classified_ids[row[0]] = row[2].split(';')

potential_ids = set()
for row in csv.reader(open('local_data/PotentialEvent.csv')):
    potential_ids.add(row[0])

a = time.time()
print "Loading fb data..."
fb_entries = {}
csv.field_size_limit(1000000000)
for i, row in enumerate(csv.reader(open('local_data/FacebookCachedObject.csv'))):
    if i % 10000 == 0:
        print 'Loading fb row %s' % i
    row_id = row[0].split('.')[1]
    if row_id in potential_ids or row_id in classified_ids:
        fb_entries[row[0]] = row[1]
print "done, %d seconds" % (time.time() - a)

all_ids = potential_ids.union(classified_ids)


def get_fb_event(id):
    EVENT_KEY = '701004.%s.OBJ_EVENT'
    key = EVENT_KEY % id
    if key not in fb_entries:
        return None
    fb_event = json.loads(fb_entries[key])
    if fb_event['deleted']:
        return None
    return fb_event

def get_types_to_ids(all_ids):
    types_to_ids = {}
    for id in all_ids:
        for type in classified_ids[id]:
            try:
                types_to_ids[type].append(id)
            except KeyError:
                types_to_ids[type] = [id]
    return types_to_ids

def get_onlytypes_to_ids(all_ids):
    types_to_ids = {}
    for id in all_ids:
        if len(classified_ids[id]) == 1:
            for type in classified_ids[id]:
                try:
                    types_to_ids[type].append(id)
                except KeyError:
                    types_to_ids[type] = [id]
    return types_to_ids

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

def get_keyword_mapping(all_ids, stripper=lambda x:x):
    keyword_mapping = {}
    for fb_id in all_ids:
        fb_event = get_fb_event(fb_id)
        if fb_event:
            search_text = (fb_event['info'].get('name', '') + ' ' + fb_event['info'].get('description', '')).lower()
        else:
            search_text = ''
        search_text = stripper(search_text)
        #TODO(lambert): also explore bigrams
        if 1:
            words = set(re.split(r'\s+', search_text))
            keyword_mapping[fb_id] = words
        else:
            words = re.split(r'\s+', search_text)
            new_words = ['%s %s' % (words[i], words[i+1]) for i in range(len(words)-1)]
            keyword_mapping[fb_id] = set(new_words)
        
    return keyword_mapping

def get_df(ids, keyword_mapping):
    words = {}
    for id in ids:
        for word in keyword_mapping[id]:
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
    print '\n'.join([x[0] for x in sorted_df(df)][:20])



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
    search_text = basic_neg_re.sub('', search_text)
    return basic_re.search(search_text)

def strip_basic_all(text):
    return basic_neg_re.sub('', basic_re.sub('', text))
def strip_basic_neg(text):
    return basic_neg_re.sub('', text)

def get_matches(fb_event):
    search_text = (fb_event['info'].get('name', '') + ' ' + fb_event['info'].get('description', '')).lower()
    return basic_re.findall(search_text), basic_neg_re.findall(search_text)

a = time.time()
print "Computing keyword counts..."
keyword_mapping = get_keyword_mapping(all_ids)
stripped_all_keyword_mapping = keyword_mapping#get_keyword_mapping(all_ids, stripper=strip_basic_all)
stripped_neg_keyword_mapping = keyword_mapping#get_keyword_mapping(all_ids, stripper=strip_basic_neg)
print "done, %d seconds" % (time.time() - a)

types_to_ids = get_types_to_ids(classified_ids)
onlytypes_to_ids = get_onlytypes_to_ids(classified_ids)

if positive_classifier:
    onlyclub_ids = set()#onlytypes_to_ids['FREESTYLE_CLUB']).union(onlytypes_to_ids['CHOREO_CLUB'])
    all_ids = all_ids.difference(onlyclub_ids)
    good_ids = set(classified_ids).difference(onlyclub_ids)
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

print "Best Positive Words:"
print_top_for_df(df_minus_df(get_df(false_negatives, stripped_all_keyword_mapping), get_df(bad_ids, stripped_all_keyword_mapping), negative_scale=10))

print "Best Negative Words:"
print_top_for_df(df_minus_df(get_df(false_positives, stripped_neg_keyword_mapping), get_df(good_ids, stripped_neg_keyword_mapping), negative_scale=0.5))

for id in false_positives:
        fb_event = get_fb_event(id)
        print 'F', id, get_matches(fb_event)

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

