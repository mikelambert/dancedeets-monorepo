import datetime

from classes import class_models
from classes import class_servlets
from classes.scraper import items
from test_utils import unittest


class _TestDedupeList(unittest.TestCase):
    studio_name = 'DummyStudio'

    def get_scrape(self, start_time=None, scrape_time=None, len=5):
        assert scrape_time
        assert start_time
        scrape_items = []
        for i in range(len):
            item = items.StudioClass()
            item['studio_name'] = self.studio_name
            this_start_time = start_time + datetime.timedelta(days=i)
            item['start_time'] = this_start_time.strftime(class_servlets.DATETIME_FORMAT)
            item['scrape_time'] = scrape_time.strftime(class_servlets.DATETIME_FORMAT)
            item['teacher'] = 'A Very Busy Teacher'
            scrape_items.append(item)
        return scrape_items

    def get_old_scrape(self, today):
        raise NotImplementedError()

    def get_new_scrape(self, today):
        raise NotImplementedError()

    def runTest(self):
        today = datetime.datetime.combine(datetime.date.today(), datetime.time())
        for item in self.get_old_scrape(today):
            class_servlets.process_uploaded_item(item)
        for item in self.get_new_scrape(today):
            class_servlets.process_uploaded_item(item)
        class_servlets.process_upload_finalization(self.studio_name)
        # Assert invariants
        self.check_classes(today)

    def check_classess(self, today):
        raise NotImplementedError()


class TestOverwriteClasses(_TestDedupeList):
    def get_old_scrape(self, today):
        return self.get_scrape(start_time=today, scrape_time=today)

    def get_new_scrape(self, today):
        return self.get_scrape(start_time=today, scrape_time=today + datetime.timedelta(hours=4))

    def check_classes(self, today):
        query = class_models.StudioClass.query()
        results = query.fetch(1000)
        self.assertEqual(len(results), 5)


class TestDeletedClass(_TestDedupeList):
    def get_old_scrape(self, today):
        print self.get_scrape(start_time=today, scrape_time=today)
        return self.get_scrape(start_time=today, scrape_time=today)

    def get_new_scrape(self, today):
        print self.get_scrape(start_time=today, scrape_time=today + datetime.timedelta(hours=4))[1:]
        return self.get_scrape(start_time=today, scrape_time=today + datetime.timedelta(hours=4))[1:]

    def check_classes(self, today):
        query = class_models.StudioClass.query()
        results = query.fetch(1000)
        start_times = [x.start_time for x in results]
        self.assertEqual(start_times, [
            today + datetime.timedelta(days=1),
            today + datetime.timedelta(days=2),
            today + datetime.timedelta(days=3),
            today + datetime.timedelta(days=4),
        ])

        self.assertEqual(len(results), 4)


class TestYesterdayIsPreserved(_TestDedupeList):
    def get_old_scrape(self, today):
        yesterday = today - datetime.timedelta(days=1)
        return self.get_scrape(start_time=yesterday, scrape_time=yesterday)

    def get_new_scrape(self, today):
        return self.get_scrape(start_time=today, scrape_time=today)

    def check_classes(self, today):
        query = class_models.StudioClass.query()
        results = query.fetch(1000)
        self.assertEqual(len(results), 6)


class TestYesterdayIsPreservedAndDeletedClass(_TestDedupeList):
    def get_old_scrape(self, today):
        yesterday = today - datetime.timedelta(days=1)
        return self.get_scrape(start_time=yesterday, scrape_time=yesterday)

    def get_new_scrape(self, today):
        return self.get_scrape(start_time=today, scrape_time=today)[1:]

    def check_classes(self, today):
        query = class_models.StudioClass.query()
        results = query.fetch(1000)
        yesterday = today - datetime.timedelta(days=1)
        start_times = [x.start_time for x in results]
        self.assertEqual(start_times, [
            yesterday,
            yesterday + datetime.timedelta(days=2),
            yesterday + datetime.timedelta(days=3),
            yesterday + datetime.timedelta(days=4),
            yesterday + datetime.timedelta(days=5),
        ])
