# Automatically created by: shub deploy

from setuptools import setup, find_packages
import glob

setup(
    name='dancedeets-scrapy',
    version='1.0',
    packages=['dancedeets.%s' % x for x in find_packages('../../server')] + find_packages(),
    package_dir={'dancedeets': '../../server'},
    install_requires=[
        # I'm not sure this really does anything more than documentation,
        # as our our dependencies need to be installed as eggs directly on dash.scrapinghub.com
        'icalendar',
        'dateparser',
        'html2text',
    ],
    data_files=[
        ('dancedeets/dance_keywords', glob.glob('nlp/dance_keywords/*.txt')),
        ('dancedeets', [
            'keys.yaml',
            'keys-dev.yaml',
            'facebook-prod.yaml',
            'facebook-test.yaml',
        ]),
    ],
    include_package_data=True,
    entry_points={'scrapy': ['settings = scrapy_settings']},
)
