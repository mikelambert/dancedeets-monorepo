#!/usr/bin/python

import commands
import download_pr_data

for x in [download_pr_data.TRIMMED_CITY_CATEGORY_DB, download_pr_data.PERSON_CITY_DB]:
    commands.getoutput('gsutil cp %s gs://dancedeets-dependencies/' % x)
