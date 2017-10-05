#!/bin/bash
#
# import google cloud datastore into sqlite

DB_PATH=$(cd ../server && python tools/download_pr_data.py db_name)
echo $DB_PATH
BOTO_PATH=../.boto gsutil cp $DB_PATH gs://dancedeets-dependencies/
