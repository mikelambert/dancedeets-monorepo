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
    ('zh-Hant', 'chinese'),
    ('zh-Hans', 'chinese'),
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
    ('id', 'indonesian'),
    ('ms', 'malay'),
    ('tl', 'tagalog'),
    ('vi', 'vietnamese'),
]


def my_repr(s):
    if "'" in s:
        return ('u"%s"' % s)
    else:
        return ("u'%s'" % s)


def translate(q):
    print '%s, # %s' % (my_repr(q), 'english')
    for language, language_name in LANGUAGES:
        service = build('translate', 'v2', developerKey=keys.get('google_server_key'))
        result = service.translations().list(target=language, format='text', q=[q]).execute()
        translations = [x['translatedText'] for x in result['translations']]
        print '%s, # %s' % (my_repr(translations[0]), language_name)


if __name__ == '__main__':
    translate(sys.argv[1])
