#!/usr/bin/python

'> training_csv.txt'

import csv
import os
import string

all_data_lines = set()
tags_data = {}

trans = string.maketrans("-/","  ")
delchars = string.punctuation.replace("-", "").replace("/", "")
def strip_punctuation(s):
    return s.translate(trans, delchars)

print "Reading training CSV source file"
for line in csv.reader(open('training/training_csv.txt')):
    tags, creator, location, text = line
    real_tags = [x for x in tags.split(' ') if x.startswith('FREESTYLE_') or x.startswith('CHOREO_')]
    data_line = (creator, strip_punctuation(location).lower(), strip_punctuation(text).lower())
    for x in real_tags:
        try:
            tags_data[x].append(data_line)
        except KeyError:
            tags_data[x] = [data_line]
    all_data_lines.add(data_line)

print "Writing training CSV files"
for key in tags_data:
    positive_results = tags_data[key]
    negative_results = all_data_lines.difference(positive_results)
    csv_writer = csv.writer(open('training/training_csv-%s.txt' % key, 'w'))
    for x in positive_results:
        csv_writer.writerow([1] + list(x))
    for x in negative_results:
        csv_writer.writerow([0] + list(x))

print "Copying to server"
os.system('gsutil cp training/training_csv-*.txt gs://dancedeets')

# java -cp oacurl-1.2.0.jar com.google.oacurl.Login --scope https://www.googleapis.com/auth/prediction

print "Triggering training for uploaded models"
for key in tags_data:
    os.system('./training/oauth-train.sh dancedeets/training_csv-%s.txt' % key)

print "Commands to run to check training status"
for key in tags_data:
    print './training/oauth-check-training.sh dancedeets/training_csv-%s.txt' % key


