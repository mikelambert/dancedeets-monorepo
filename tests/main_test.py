#!/usr/bin/python
# why do we have to put this in the util directory? why won't it work as a nosetest from the root directory?

import unittest

class ImportTest(unittest.TestCase):
    def test_main_import(self):
        import main

if __name__ == '__main__':
    unittest.main()
