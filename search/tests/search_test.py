from webtest import TestApp

import main
from test_utils import unittest

app = TestApp(main.application)

class TestSearch(unittest.TestCase):
    def runTest(self):
        app.get('/?location=New York&distance=50')
