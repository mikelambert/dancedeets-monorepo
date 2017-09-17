# Automatically created by: shub deploy

from setuptools import setup, find_packages
import glob

setup(
    name='dancedeets-scrapy',
    version='1.0',
    packages=['dancedeets'] + find_packages(),
    package_dir={'dancedeets': '../../server'},
    install_requires=[
        # I'm not sure this really does anything more than documentation,
        # as our our dependencies need to be installed as eggs directly on dash.scrapinghub.com
        'icalendar',
        'dateparser',
        'html2text',
    ],
    entry_points={'scrapy': ['settings = scrapy_settings']},
)
