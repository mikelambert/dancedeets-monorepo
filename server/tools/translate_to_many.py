#!/usr/bin/python

import sys

from dancedeets import runner

runner.setup()

from googleapiclient.discovery import build
from dancedeets import keys

LANGUAGES = [
    #
    ('es', 'spanish'),
    ('fr', 'french'),
    ('it', 'italian'),
    ('pt', 'portuguese'),
    #
    ('de', 'german'),
    ('pl', 'polish'),
    ('da', 'danish'),
    ('nl', 'dutch'),
    ('lt', 'lithuanian'),
    #
    ('fi', 'finnish'),
    ('sv', 'swedish'),
    ('no', 'norwegian'),
    #
    ('ja', 'japanese'),
    ('ko', 'korean'),
    ('zh-Hant', 'chinese traditional'),
    ('zh-Hans', 'chinese simplified'),
    #
    ('ar', 'arabic'),
    ('he', 'hebrew'),
    #
    ('cs', 'czech'),
    ('el', 'greek'),
    ('tr', 'turkish'),
    ('hu', 'hungarian'),
    ('ru', 'russian'),
    ('hr', 'croatian'),
    ('mk', 'macedonian'),
    ('ro', 'romanian'),
    #
    # not popular enough
    #('bn', 'bengali'),
    #('pa', 'punjabi'),
    ('ms', 'malay'),
    ('tl', 'tagalog'),
    ('vi', 'vietnamese'),
    ('th', 'thai'),
]


def my_repr(s):
    if "'" in s:
        return ('u"%s"' % s)
    else:
        return ("u'%s'" % s)


def translate(queries):
    service = build('translate', 'v2', developerKey=keys.get('google_server_key'))

    translations = {}
    for q in queries:
        translations[my_repr(q.lower())] = 'english'
        for language, language_name in LANGUAGES:
            result = service.translations().list(source='en', target=language, format='text', q=[q]).execute()
            result_translations = [x['translatedText'] for x in result['translations']]
            translation = my_repr(result_translations[0].lower())
            translations[translation] = language_name

    print '\n'.join(sorted('%s, # %s' % x for x in translations.items()))


if __name__ == '__main__':
    translate(sys.argv[1:])
