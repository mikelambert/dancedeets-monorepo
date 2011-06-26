import datetime
import unittest
from util import dates

class DatesTest(unittest.TestCase):
    def test_localize_timestamp(self):
        fb_new_years = datetime.datetime(2000, 1, 1, 8)
        real_new_years = dates.localize_timestamp(fb_new_years)
        self.assertEqual(real_new_years, datetime.datetime(2000, 1, 1))

    def test_parse_fb_timestamp(self):
        # assert we don't crash
        dates.parse_fb_timestamp(None)

        # If it's raw stuff as comes from fb, return it exactly
        self.assertEqual(datetime.datetime(2000, 1, 1),
                         dates.parse_fb_timestamp('2000-01-01T00:00:00'))

        # Otherwise convert timezones
        self.assertEqual(datetime.datetime(2000, 1, 1),
                         dates.parse_fb_timestamp('2000-01-01T08:00:00+0000'))


if __name__ == '__main__':
    unittest.main()
