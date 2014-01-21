#!/usr/bin/python
# why do we have to put this in the util directory? why won't it work as a nosetest from the root directory?

import unittest
import webapp2

class TestImports(unittest.TestCase):
    def runTest(self):
        import main

class TestUrlRoutes(unittest.TestCase):
    def runTest(self):
        import main
        from servlets import event
        router = webapp2.Router(main.URLS)
        env = {'PATH_INFO': '/events/55/'}
        route = router.match(webapp2.Request(env))
        self.assertEqual(route[0].handler, event.ShowEventHandler)

if __name__ == '__main__':
    unittest.main()
