from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner

from classes import class_pipeline
from test_utils import unittest


class TestSpiderList(unittest.TestCase):
    def runTest(self):
        settings = get_project_settings()
        settings.set('SPIDER_MODULES', ['classes.scraper.spiders'])
        runner = CrawlerRunner(settings)
        spiders = runner.spider_loader.list()
        self.assertEqual(set(class_pipeline.get_spiders()), set(spiders))
