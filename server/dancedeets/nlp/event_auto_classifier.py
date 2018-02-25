# -*-*- encoding: utf-8 -*-*-

from dancedeets.nlp import styles
from dancedeets.nlp.street import classifier as street_classifier


def is_auto_add_event(classified_event):
    c = AutoClassifier(classified_event)
    c.classify()
    return c


class AutoClassifier(object):
    def __init__(self, classified_event):
        self.classified_event = classified_event
        self.result = None

    def __repr__(self):
        return repr(self.result)

    def _run_classify(self):
        results = []
        for classifier in styles.CLASSIFIERS.values():
            this_classifier = classifier(self.classified_event)
            is_dance_event = this_classifier.is_dance_event()
            if is_dance_event:
                results.append((is_dance_event, this_classifier.debug_info(), this_classifier.vertical))

        self._reasons = [x[1] for x in results]
        self._verticals = [x[2] for x in results]

        if self._verticals:
            return (True, 'found some:\n%s' % self._reasons, self._verticals)

        return (False, 'nothing', [])

    def classify(self):
        self.result = self._run_classify()

    def is_good_event(self):
        return self.result[0]

    def reason(self):
        return self.result[1]

    def reasons(self):
        return self._reasons

    def verticals(self):
        return self._verticals


def is_auto_notadd_event(classified_event, auto_add_result=None):
    c = auto_add_result or is_auto_add_event(classified_event)
    if c.is_good_event():
        return False, 'is auto_add_event: %s' % c.reason()

    result = street_classifier.is_bad_club(classified_event)
    if result[0]:
        return result
    result = street_classifier.is_bad_wrong_dance(classified_event)
    if result[0]:
        return result
    return False, 'not a bad enough event'
