#!/usr/bin/python
# -*-*- encoding: utf-8 -*-*-

import csv
import re
import os
from logic import event_manual_classifier
from events import tags


all_data_lines = set()
tags_data = {}

print "Reading training CSV source file"
cevents = []
for line in csv.reader(open('training/training_csv.txt')):
    event_tags, creator, location, text = line
    real_tags = [x for x in event_tags.split(' ') if x.startswith('FREESTYLE_') or x.startswith('CHOREO_')]
    fake_fb_event = dict(info=dict(owner=dict(id=creator),name='',description=text,location=location))
    cevent = event_manual_classifier.ClassifyEvent(fake_fb_event)

    for x in real_tags:
        try:
            tags_data[x].append(cevent)
        except KeyError:
            tags_data[x] = [cevent]
    all_data_lines.add(cevent)

print "Writing training CSV files"
positive_negative_cevents = {}
for key in tags_data:
    positive = tags_data[key]
    negative = all_data_lines.difference(positive)
    positive_negative_cevents[key] = (positive, negative)

#match_list = [(matchop, matchfield, text_or_regex), ...]
def test_match_on_data(tag, match_list):
    true_positives = []
    false_positives = []

    positive, negative = positive_negative_cevents[tag]
    for p_cevent in positive:
        result = p_cevent.match(match_list)
        if result:
            true_positives.append(result)
    for n_cevent in negative:
        result = n_cevent.match(match_list)
        if result:
            false_positives.append(result)
    return true_positives, false_positives

# (tag, [(matchop, matchfield, text_or_regex), ...])
#[(ems.MATCH_OP_REGEX, ems.MATCH_FIELD_ALL_TEXT, re.compile(r'\d+[ -]?(?:vs?\.?|x|×|on)[ -]?\d+'))])
ems = event_manual_classifier
tag_and_match_details = [
    (tags.FREESTYLE_COMPETITION, [ems.NvsN])
]

for tag, match_list in tag_and_match_details:
    true_positives, false_positives = test_match_on_data(tag, match_list)
    print true_positives
    print false_positives
    print "Evaluating:", tag, match_list
    print "  Results: %s classified, %s false positives: %s" %(len(true_positives), len(false_positives), false_positives)


