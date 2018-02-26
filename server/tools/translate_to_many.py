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
    ('sk', 'slovak'),
    ('el', 'greek'),
    ('tr', 'turkish'),
    ('hu', 'hungarian'),
    ('ru', 'russian'),
    #
    ('bn', 'bengali'),
    ('pa', 'punjabi'),
    ('id', 'indonesian'),
    ('ms', 'malay'),
    ('tl', 'tagalog'),
    ('vi', 'vietnamese'),
    ('th', 'thailand'),
]


def my_repr(s):
    if "'" in s:
        return ('u"%s"' % s)
    else:
        return ("u'%s'" % s)


def translate(queries):
    service = build('translate', 'v2', developerKey=keys.get('google_server_key'))

    translations = []
    for q in queries:
        translations.append('%s, # %s' % (my_repr(q).lower(), 'english'))
        for language, language_name in LANGUAGES:
            result = service.translations().list(target=language, format='text', q=[q]).execute()
            result_translations = [x['translatedText'] for x in result['translations']]
            translations.append('%s, # %s' % (my_repr(result_translations[0]).lower(), language_name))
    print '\n'.join(sorted(translations))


if __name__ == '__main__':
    translate(sys.argv[1:])
