#!/usr/bin/python

import commands
import os

import download_pr_data

for x in ['pr_city_category.db', 'pr_person_city.db', 'cities.db']:
    db_filename = os.path.join(download_pr_data.DB_PATH, x)
    commands.getoutput('gsutil cp %s gs://dancedeets-dependencies/' % db_filename)
