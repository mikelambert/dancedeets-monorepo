rm events.txt
appcfg.py download_data --application=dancedeets --kind="DBEvent" --url=http://dancedeets.appspot.com/remote_api --filename=events.db
appcfg.py download_data --application=dancedeets --kind="(DBEvent,FacebookCachedObject)" --url=http://dancedeets.appspot.com/remote_api --filename=all_events_data.db
appcfg.py upload_data --application=dancedeets --kind="(DBEvent,FacebookCachedObject)" --url=http://127.0.0.1:8080/remote_api --filename=all_events_data.db
rm bulkloader-*
