# Automatically created by: shub deploy

from setuptools import setup, find_packages
import glob

packages = (
    ['dancedeets'] +
    ['dancedeets.%s' % x for x in find_packages('../../server')] +
    find_packages()
)

setup(
    name='dancedeets-scrapy',
    version='1.0',
    packages=packages,
    package_dir={'dancedeets': '../../server'},
    install_requires=[
        # I'm not sure this really does anything more than documentation,
        # as our our dependencies need to be installed as eggs directly on dash.scrapinghub.com
        'icalendar',
        'dateparser',
        'html2text',
    ],
    py_modules=[
        'scrapy_settings',
    ],
    data_files=[
        ('dancedeets/nlp/dance_keywords', glob.glob('../../server/nlp/dance_keywords/*.txt')),
        ('dancedeets', [
            '../../server/keys.yaml',
            '../../server/keys-dev.yaml',
            '../../server/facebook-prod.yaml',
            '../../server/facebook-test.yaml',
        ]),
    ],
    include_package_data=True,
    entry_points={'scrapy': ['settings = scrapy_settings']},
)
