import fb_api
import fb_api_util

from test_utils import unittest


class TestLookupUser(unittest.TestCase):
    def runTest(self):
        ids = ['110312662362915']
        fbl = fb_api.FBLookup(None, None)
        page_ids = fb_api_util.filter_by_type(fbl, ids, 'page')
        self.assertEqual(page_ids, ids)
