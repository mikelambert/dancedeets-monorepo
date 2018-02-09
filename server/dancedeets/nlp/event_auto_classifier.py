# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .street import classifier as street_classifier
from .latin import classifier as latin_classifier


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
        result = latin_classifier.is_salsa_event(self.classified_event)
        if result[0]:
            return result

        result = street_classifier.is_street_event(self.classified_event)
        if result[0]:
            return result

        return (False, 'nothing', [])

    def classify(self):
        self.result = self._run_classify()

    def is_good_event(self):
        return self.result[0]

    def reason(self):
        return self.result[1]

    def verticals(self):
        try:
            return self.result[2]
        except:
            return [event_types.VERTICALS.STREET]


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
