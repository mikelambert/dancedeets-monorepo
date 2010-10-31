rm bulkloader*
rm mapreducestates.db
rm events.db
rm potentialevents.db
rm fb_data.db
appcfg.py download_data --application=dancedeets --kind="MapreduceState" --url=http://dancedeets.appspot.com/_ah/remote_api --filename=mapreducestates.db
appcfg.py download_data --application=dancedeets --kind="DBEvent" --url=http://dancedeets.appspot.com/_ah/remote_api --filename=events.db
appcfg.py download_data --application=dancedeets --kind="PotentialEvent" --url=http://dancedeets.appspot.com/_ah/remote_api --filename=potentialevents.db
appcfg.py download_data --application=dancedeets --kind="FacebookCachedObject" --url=http://dancedeets.appspot.com/_ah/remote_api --filename=fb_data.db
appcfg.py upload_data --application=dancedeets --kind="MapreduceState" --url=http://127.0.0.1:8080/_ah/remote_api --filename=mapreducestates.db
appcfg.py upload_data --application=dancedeets --kind="DBEvent" --url=http://127.0.0.1:8080/_ah/remote_api --filename=events.db
appcfg.py upload_data --application=dancedeets --kind="PotentialEvent" --url=http://127.0.0.1:8080/_ah/remote_api --filename=potentialevents.db
appcfg.py upload_data --application=dancedeets --kind="FacebookCachedObject" --url=http://127.0.0.1:8080/_ah/remote_api --filename=fb_data.db
rm bulkloader-*
