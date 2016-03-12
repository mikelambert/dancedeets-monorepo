# Automatically created by: shub deploy

from setuptools import setup, find_packages
import glob

setup(
    name='project',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        # I'm not sure this really does anything more than documentation,
        # as our our dependencies need to be installed as eggs directly on dash.scrapinghub.com
        'icalendar',
        'dateparser',
        'html2text',
    ],
    py_modules=[
        'event_types',
        'keys',
        'mindbody',
        'styles',
        'scrapy_settings',
    ],
    data_files=[
        ('dance_keywords', glob.glob('dance_keywords/*.txt')),
        ('', ['keys.yaml']),
    ],
    include_package_data=True,
    entry_points={'scrapy': ['settings = scrapy_settings']},
)
