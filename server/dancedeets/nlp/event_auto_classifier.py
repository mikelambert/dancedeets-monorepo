# -*-*- encoding: utf-8 -*-*-

from dancedeets import event_types
from .african import classifier as african_classifier
from .ballroom import classifier as ballroom_classifier
from .capoeira import classifier as capoeira_classifier
from .contact import classifier as contact_classifier
from .country import classifier as country_classifier
from .latin import classifier as latin_classifier
from .partner_fusion import classifier as partner_fusion_classifier
from .rockabilly import classifier as rockabilly_classifier
from .street import classifier as street_classifier
from .swing import classifier as swing_classifier
from .tango import classifier as tango_classifier
from .wcs import classifier as wcs_classifier
from .zouk import classifier as zouk_classifier


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

        classifiers = [
            ballroom_classifier.is_ballroom_event,
            capoeira_classifier.is_capoeira_event,
            country_classifier.is_country_event,
            latin_classifier.is_salsa_event,
            partner_fusion_classifier.is_fusion_event,
            rockabilly_classifier.is_rockabilly_event,
            street_classifier.is_street_event,
            swing_classifier.is_swing_event,
            tango_classifier.is_tango_dance,
            wcs_classifier.is_wcs_event,
            zouk_classifier.is_zouk_dance,
            contact_classifier.is_contact_improv_event,
            african_classifier.is_african_event,
        ]
        for classifier in classifiers:
            result = classifier(self.classified_event)
            if result[0]:
                results.append(result)

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
