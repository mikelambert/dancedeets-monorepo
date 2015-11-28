#!/usr/bin/python

import unittest

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner

from classes import class_pipeline

class TestSpiderList(unittest.TestCase):
    def runTest(self):
        runner = CrawlerRunner(get_project_settings())
        spiders = runner.spider_loader.list()
        self.assertEqual(set(class_pipeline.get_spiders()), set(spiders))

if __name__ == '__main__':
    unittest.main()
