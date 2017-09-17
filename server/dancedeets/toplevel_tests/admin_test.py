#!/usr/bin/python

import unittest

from dancedeets import admin


class TestAdmin(unittest.TestCase):
    def runTest(self):
        self.assert_(admin.admin)
