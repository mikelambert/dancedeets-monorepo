#!/usr/bin/python

import unittest

import admin

class TestAdmin(unittest.TestCase):
    def runTest(self):
        self.assert_(admin.admin)
