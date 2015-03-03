import csv
import json
import multiprocessing
import os

# grep '^701004.[0-9]*.OBJ_EVENT,' local_data/FacebookCachedObject.csv > local_data/FacebookCachedObjectEvent.csv

class ClassifiedIds(object):
    def __init__(self, good_ids, bad_ids):
        self.good_ids = frozenset(good_ids)
        self.bad_ids = frozenset(bad_ids)

class ClassifierScoreCard(object):
    def __init__(self, training_data, classifier_data, positive_classifier):
        if positive_classifier:
            good_ids = training_data.good_ids
            bad_ids = training_data.bad_ids
        else:
            bad_ids = training_data.good_ids
            good_ids = training_data.bad_ids

        self.false_positives = classifier_data.good_ids.difference(good_ids)
        self.false_negatives = classifier_data.bad_ids.difference(bad_ids)
        self.true_positives = classifier_data.good_ids.difference(bad_ids)
        self.true_negatives = classifier_data.bad_ids.difference(good_ids)

    def write_to_disk(self, directory):
        try:
            os.makedirs(directory)
        except OSError:
            pass
        open(os.path.join(directory, 'false_positives.txt'), 'w').writelines('%s\n' % x for x in sorted(self.false_positives))
        open(os.path.join(directory, 'false_negatives.txt'), 'w').writelines('%s\n' % x for x in sorted(self.false_negatives))
        open(os.path.join(directory, 'true_positives.txt'), 'w').writelines('%s\n' % x for x in sorted(self.true_positives))
        open(os.path.join(directory, 'true_negatives.txt'), 'w').writelines('%s\n' % x for x in sorted(self.true_negatives))



def _partition_classify(arg):
    classifier, (key, value) = arg
    result = classifier(value)
    return (result, key)

def _partition_init_worker():
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    import os
    os.nice(5)

def partition_data(data, classifier=lambda x:False, workers=None):
    if not workers:
        workers = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=workers, initializer=_partition_init_worker)
    print "Generating data..."
    data = [(classifier, x) for x in data]
    print "Running multiprocessing classifier..."
    async_results = pool.map_async(_partition_classify, data, chunksize=100)
    # We need to specify a timeout to get(), so that KeyboardInterrupt gets delivered properly.
    results = async_results.get(9999999)
    print "Multiprocessing classifier completed."
    successes = set(x[1] for x in results if x[0])
    fails = set(x[1] for x in results if not x[0])
    return ClassifiedIds(successes, fails)


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


