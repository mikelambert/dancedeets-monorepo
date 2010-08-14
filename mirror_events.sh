rm events.txt
appcfg.py download_data --application=dancedeets --kind=DBEvent --url=http://dancedeets.appspot.com/remote_api --filename=events.txt
appcfg.py upload_data --application=dancedeets --kind=DBEvent --url=http://127.0.0.1:8080/remote_api --filename=events.txt
rm bulkloader-*
