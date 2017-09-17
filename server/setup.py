# Automatically created by: shub deploy

from setuptools import setup, find_packages
import glob

# This basically packages up the dancedeets package, for use by dancedeets-scrapy
# it doesn't package up the entirety of dancedeets, however.
setup(
    name='dancedeets',
    version='1.0',
    packages=find_packages(),
    py_modules=[
        'event_types',
        'facebook',
        'keys',
        'mindbody',
        'styles',
        'scrapy_settings',
    ],
    data_files=[
        ('dance_keywords', glob.glob('nlp/dance_keywords/*.txt')),
        ('', [
            'keys.yaml',
            'keys-dev.yaml',
            'facebook-prod.yaml',
            'facebook-test.yaml',
        ]),
    ],
    include_package_data=True,
)
