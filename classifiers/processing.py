import csv
import json

# grep '^701004.[0-9]*.OBJ_EVENT,' local_data/FacebookCachedObject.csv > local_data/FacebookCachedObjectEvent.csv

class ClassifiedIds(object):
    def __init__(self, good_ids, bad_ids):
        self.good_ids = frozenset(good_ids)
        self.bad_ids = frozenset(bad_ids)

def load_all_ids():
    result = set()
    for row in csv.reader(open('local_data/DBEvent.csv')):
        result.add(row[0])
    for row in csv.reader(open('local_data/PotentialEvent.csv')):
        result.add(row[0])
    return result


def load_classified_ids(all_ids):
    good_ids = set()
    for row in csv.reader(open('local_data/DBEvent.csv')):
        good_ids.add(row[0])

    for line in open('local_data/added_ids.txt').readlines():
        line = line.strip()
        good_ids.add(line)

    for line in open('local_data/diffs.txt').readlines():
        line = line.strip()
        if line.startswith('+'):
            good_ids.add(line[1:])
        elif line.startswith('-'):
            good_ids.remove(line[1:])

    bad_ids = all_ids.difference(good_ids)
    classified_ids = ClassifiedIds(good_ids, bad_ids)
    return classified_ids

def all_fb_data(combined_ids, filename='local_data/FacebookCachedObjectEvent.csv'):
    csv.field_size_limit(1000000000)
    for row in csv.reader(open(filename)):
        source_id, row_id, row_type = row[0].split('.')
        if source_id == "701004" and row_type == 'OBJ_EVENT' and (not combined_ids or row_id in combined_ids):
            fb_event = json.loads(row[1])
            if fb_event and not fb_event.get('deleted') and not fb_event.get('empty') and fb_event['info'].get('privacy', 'OPEN') == 'OPEN':
                yield row_id, fb_event


