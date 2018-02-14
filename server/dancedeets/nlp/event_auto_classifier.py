# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .ballroom import classifier as ballroom_classifier
from .capoeira import classifier as capoeira_classifier
from .latin import classifier as latin_classifier
from .street import classifier as street_classifier
from .swing import classifier as swing_classifier


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
        verticals = []

        result = latin_classifier.is_salsa_event(self.classified_event)
        if result[0]:
            verticals.append(result[2])

        result = street_classifier.is_street_event(self.classified_event)
        if result[0]:
            verticals.append(result[2])

        result = capoeira_classifier.is_capoeira_event(self.classified_event)
        if result[0]:
            verticals.append(result[2])

        result = ballroom_classifier.is_ballroom_event(self.classified_event)
        if result[0]:
            verticals.append(result[2])

        result = swing_classifier.is_swing_event(self.classified_event)
        if result[0]:
            verticals.append(result[2])

        result = street_classifier.is_street_event(self.classified_event)
        if result[0]:
            verticals.append(result[2])

        if verticals:
            return (True, 'found some', verticals)

        return (False, 'nothing', [])

    def classify(self):
        self.result = self._run_classify()

    def is_good_event(self):
        return self.result[0]

    def reason(self):
        return self.result[1]

    def verticals(self):
        return self.result[2]


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
