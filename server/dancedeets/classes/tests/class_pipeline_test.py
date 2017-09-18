from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner

from dancedeets.classes import class_pipeline
from dancedeets.test_utils import unittest


class TestSpiderList(unittest.TestCase):
    def runTest(self):
        settings = get_project_settings()
        settings.set('SPIDER_MODULES', ['classes.spiders'])
        runner = CrawlerRunner(settings)
        spiders = runner.spider_loader.list()
        print class_pipeline.get_spiders()
        print spiders
        self.assertEqual(set(class_pipeline.get_spiders()), set(spiders))
