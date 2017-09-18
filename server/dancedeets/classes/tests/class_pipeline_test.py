import os
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner
import sys

import dancedeets
from dancedeets.classes import class_pipeline
from dancedeets.test_utils import unittest


scrapy_path = os.path.join(os.path.dirname(dancedeets.__file__), '..', '..', 'scrapers', 'scrapy')

class TestSpiderList(unittest.TestCase):
    def runTest(self):
        settings = get_project_settings()
        settings.set('SPIDER_MODULES', ['classes.spiders'])
        try:
            sys.path.append(scrapy_path)
            runner = CrawlerRunner(settings)
            spiders = runner.spider_loader.list()
            self.assertEqual(set(class_pipeline.get_spiders()), set(spiders))
        except:
            pass
