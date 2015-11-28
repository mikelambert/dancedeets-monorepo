# Automatically created by: shub deploy

from setuptools import setup, find_packages
import glob

setup(
    name         = 'project',
    version      = '1.0',
    packages     = find_packages(),
    install_requires = [
        'icalendar',
        'dateparser',
    ],
    py_modules = [
        'event_types',
        'keys',
        'mindbody',
        'styles',
    ],
    data_files   = [
        ('dance_keywords', glob.glob('dance_keywords/*.txt')),
        ('', ['keys.yaml']),
    ],
    include_package_data=True,
    entry_points = {'scraper': ['settings = classes.scraper.settings']},
)
