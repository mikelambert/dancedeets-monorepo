import csv
import json

def load_ids():
    result = {}
    result['good_ids'] = set()
    for row in csv.reader(open('local_data/DBEvent.csv')):
        result['good_ids'].add(row[0])

    result['potential_ids'] = set()
    for row in csv.reader(open('local_data/PotentialEvent.csv')):
        result['potential_ids'].add(row[0])

    result['combined_ids'] = result['potential_ids'].union(result['good_ids'])

    result['bad_ids'] = result['combined_ids'].difference(result['good_ids'])

    for line in open('local_data.diffs.txt').readlines()
        if line.startswith('+'):
            result['good_ids'].add(line[1:])
            result['bad_ids'].remove(line[1:])
        elif line.startswith('-'):
            result['good_ids'].remove(line[1:])
            result['bad_ids'].add(line[1:])

    return result


def all_fb_data(combined_ids):
    csv.field_size_limit(1000000000)
    for row in csv.reader(open('local_data/FacebookCachedObject.csv')):
        source_id, row_id, row_type = row[0].split('.')
        if source_id == "701004" and row_type == 'OBJ_EVENT' and row_id in combined_ids:
            fb_event = json.loads(row[1])
            if fb_event and not fb_event['deleted'] and fb_event['info']['privacy'] == 'OPEN':
                yield row_id, fb_event


