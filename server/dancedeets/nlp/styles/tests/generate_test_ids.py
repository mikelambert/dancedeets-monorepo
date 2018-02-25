# -*-*- encoding: utf-8 -*-*-

import logging
import os
import time

logging.basicConfig(level=logging.INFO)

from dancedeets import runner

runner.setup()

from dancedeets import fb_api
from dancedeets.event_scraper import keyword_search
from dancedeets.nlp import styles
from dancedeets.test_utils import unittest

TEST_IDS_PATH = os.path.join(os.path.dirname(styles.__file__), 'test_ids')


def load_for(style_name, fbl):
    all_ids = set()
    chunks = keyword_search.get_chunks(style_name)
    for chunk in chunks:
        all_keywords = keyword_search.expand_chunk(chunk)
        for query in all_keywords:
            logging.info('Loading %s', query)
            ids = keyword_search.get_ids_for_keyword(fbl, query)
            time.sleep(2)
            all_ids.update(ids)
    return all_ids


def write_ids(filename, style_name, ids):
    f = open(filename, 'w')
    for id in ids:
        f.write('%s:%s\n' % (style_name, id))
    f.close()


def main():
    style_name = 'HUSTLE'

    filename = os.path.join(TEST_IDS_PATH, '%s.txt' % style_name)
    if os.path.exists(filename):
        raise Exception('File already exists: %s' % filename)

    fbl = fb_api.FBLookup("dummyid", unittest.get_local_access_token_for_testing())
    fbl.make_passthrough()

    all_ids = load_for(style_name, fbl)
    write_ids(filename, style_name, all_ids)


if __name__ == '__main__':
    main()
