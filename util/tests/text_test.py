import unittest
from util import text

class TestLinkify(unittest.TestCase):
    def testLinkify(self):
        link = '<a href="http://www.dancedeets.com/">'
        self.assertRegexpMatches(text.linkify('Check out http://www.dancedeets.com/ for events.'), link)
        self.assertRegexpMatches(text.linkify('Check out www.dancedeets.com/ for events.'), link)


if __name__ == '__main__':
    unittest.main()
