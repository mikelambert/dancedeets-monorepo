import datetime
import unittest
from util import dates

class TestDates(unittest.TestCase):
    nye = datetime.datetime(2000, 1, 1)
    nye_plus_8 = datetime.datetime(2000, 1, 1, 8)
    nye_plus_15 = datetime.datetime(2000, 1, 1, 15)
    nye_plus_2_days_plus_8 = datetime.datetime(2000, 1, 3, 8)

    def test_parse_fb_timestamp(self):
        # assert we don't crash
        dates.parse_fb_timestamp(None)

        # If it's raw stuff as comes from fb, return it exactly
        self.assertEqual(self.nye, dates.parse_fb_timestamp('2000-01-01T00:00:00'))

        # Otherwise convert timezones
        self.assertEqual(self.nye_plus_8, dates.parse_fb_timestamp('2000-01-01T08:00:00+0000'))

    def test_time_human_format(self):
        self.assertEqual(dates.time_human_format(self.nye),
                         '12:00am')
        self.assertEqual(dates.time_human_format(self.nye, country='UK'),
                         '0:00')
        self.assertEqual(dates.time_human_format(self.nye_plus_15),
                         '3:00pm')
        self.assertEqual(dates.time_human_format(self.nye_plus_15, country='UK'),
                         '15:00')

    def test_date_human_format(self):
        self.assertEqual(dates.date_human_format(self.nye),
                         'Saturday, January 1 - 12:00am')

    def test_duration_human_format(self):
        self.assertEqual(dates.duration_human_format(self.nye, self.nye_plus_8),
                         'Saturday, January 1 - 12:00am to 8:00am')
        self.assertEqual(dates.duration_human_format(self.nye, self.nye_plus_2_days_plus_8),
                         'Saturday, January 1 - 12:00am to Monday, January 3 - 8:00am')


    def test_event_dates(self):
        e = {'timezone_offset': 9, 'info': {'start_time': '2012-04-18T05:30:00T-0800', 'timezone': 'America/Los_Angeles'}}
        self.assertEqual(dates.parse_fb_start_time(e),
                         datetime.datetime(2012, 4, 18, 5, 30))
        e = {'timezone_offset': 9, 'info': {'start_time': '2012-04-17T13:30:00'}}
        self.assertEqual(dates.parse_fb_start_time(e),
                         datetime.datetime(2012, 4, 17, 13, 30))
if __name__ == '__main__':
    unittest.main()
