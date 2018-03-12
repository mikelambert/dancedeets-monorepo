#!/usr/bin/python

import argparse
import re

from dancedeets import runner

runner.setup()

from googleapiclient.discovery import build
from dancedeets import keys
from dancedeets.nlp import dance_keywords
from dancedeets.nlp import grammar

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


dance_re = re.compile(dance_keywords.EASY_DANCE.as_expanded_regex())
connector_re = re.compile(grammar.CONNECTOR.as_expanded_regex())


def canonicalize(translation, options):
    translation = translation.lower()
    if options.no_dance:
        translation = dance_re.sub('', translation)
        translation = connector_re.sub('', translation).strip()
    return translation


def translate(options):
    queries = options.keywords
    service = build('translate', 'v2', developerKey=keys.get('google_server_key'))

    translations = {}
    for q in queries:
        for language, language_name in LANGUAGES:
            result = service.translations().list(source='en', target=language, format='text', q=[q]).execute()
            result_translations = [x['translatedText'] for x in result['translations']]
            translation = result_translations[0].lower()
            translation_repr = my_repr(canonicalize(translation, options))
            translations.setdefault(translation_repr, []).append(language_name)
        translation_repr = my_repr(canonicalize(q, options))
        translations.setdefault(translation_repr, []).append('english')

    print '\n'.join(sorted('%s, # %s' % (k, ', '.join(sorted(v))) for (k, v) in translations.items()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-dance', '-n', help='remove dance from keywords', action='store_true')
    parser.add_argument('keywords', nargs='*')
    args = parser.parse_args()

    translate(args)


if __name__ == '__main__':
    main()
