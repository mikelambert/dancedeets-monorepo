#!/usr/bin/python

import unittest
import webapp2


class TestImports(unittest.TestCase):
    def runTest(self):
        import main
        return main  # to avoid pyflakes unused warning


class TestUrlRoutes(unittest.TestCase):
    def runTest(self):
        from dancedeets.servlets import event
        from dancedeets.app import app
        router = app.router
        env = {
            'SERVER_NAME': 'dev.dancedeets.com',
            'SERVER_PORT': '80',
            'PATH_INFO': '/events/55/',
        }
        route = router.match(webapp2.Request(env))
        self.assertEqual(route[0].handler, event.ShowEventHandler)


if __name__ == '__main__':
    unittest.main()
