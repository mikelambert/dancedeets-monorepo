#!/usr/bin/python

import os
import subprocess

import download_pr_data

for x in ['pr_city_category.db', 'pr_person_city.db', 'cities.db']:
    db_filename = os.path.join(download_pr_data.DB_PATH, x)
    print('Uploading:', x)
    subprocess.run(['gsutil', 'cp', db_filename, 'gs://dancedeets-dependencies/'])
