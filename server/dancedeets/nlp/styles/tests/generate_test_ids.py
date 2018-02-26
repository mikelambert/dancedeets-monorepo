#!/usr/bin/python
# -*-*- encoding: utf-8 -*-*-

import logging
import os
import sys
import time

logging.basicConfig(level=logging.INFO)

from dancedeets import runner

runner.setup()

from dancedeets import fb_api
from dancedeets.event_scraper import keyword_search
from dancedeets.test_utils import unittest
from dancedeets.nlp.styles.tests import util

TEST_IDS_PATH = util.TEST_IDS_PATH


def load_for(style_name, fbl):
    all_ids = set()
    chunks = keyword_search.get_chunks(style_name)
    for chunk in chunks:
        all_keywords = keyword_search.expand_chunk(chunk)
        for query in all_keywords:
            logging.info('Loading %s', query)
            id_titles = keyword_search.get_id_titles_for_keyword(fbl, query)
            time.sleep(2)
            all_ids.update('%s # %s: %s' % (x['id'], query, x['name']) for x in id_titles)
    return all_ids


def write_ids(filename, style_name, ids):
    f = open(filename, 'w')
    for id in ids:
        f.write('%s:%s\n' % (style_name, id.encode('utf-8')))
    f.close()


def main(style_name):

    filename = os.path.join(TEST_IDS_PATH, '%s.txt' % style_name)
    if os.path.exists(filename):
        raise Exception('File already exists: %s' % filename)

    fbl = fb_api.FBLookup("dummyid", unittest.get_local_access_token_for_testing())
    fbl.make_passthrough()

    all_ids = load_for(style_name, fbl)
    write_ids(filename, style_name, all_ids)


if __name__ == '__main__':
    main(sys.argv[1])
