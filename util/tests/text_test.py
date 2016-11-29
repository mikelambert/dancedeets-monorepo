import unittest
from util import text


class TestLinkify(unittest.TestCase):
    def testLinkify(self):
        link = '<a href="http://www.dancedeets.com/">'
        self.assertRegexpMatches(text.linkify('Check out http://www.dancedeets.com/ for events.'), link)
        self.assertRegexpMatches(text.linkify('Check out www.dancedeets.com/ for events.'), link)


class TestHumanList(unittest.TestCase):
    def testHumanList(self):
        self.assertEqual('0', text.human_list(range(1)))
        self.assertEqual('0 and 1', text.human_list(range(2)))
        self.assertEqual('0, 1, and 2', text.human_list(range(3)))


if __name__ == '__main__':
    unittest.main()
