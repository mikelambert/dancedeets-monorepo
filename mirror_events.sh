rm bulkloader*
rm local_data/events.db-new
rm local_data/potentialevents.db-new
rm local_data/fb_data.db-new
rm local_data/city.db-new
rm local_data/geocode.db-new
rm local_data/locationmapping.db-new
rm local_data/source.db-new
appcfg.py download_data --application=dancedeets --kind="DBEvent" --url=http://dancedeets.appspot.com/_ah/remote_api --filename=local_data/events.db-new
mv local_data/events.db{-new,}
appcfg.py download_data --application=dancedeets --kind="PotentialEvent" --url=http://dancedeets.appspot.com/_ah/remote_api --filename=local_data/potentialevents.db-new
mv local_data/potentialevents.db{-new,}
appcfg.py download_data --application=dancedeets --kind="FacebookCachedObject" --url=http://dancedeets.appspot.com/_ah/remote_api --filename=local_data/fb_data.db-new
mv local_data/fb_data.db{-new,}
#appcfg.py download_data --application=dancedeets --kind="City" --url=http://dancedeets.appspot.com/_ah/remote_api --filename=local_data/city.db-new
#mv local_data/city.db{-new,}
appcfg.py download_data --application=dancedeets --kind="Geocode" --url=http://dancedeets.appspot.com/_ah/remote_api --filename=local_data/geocode.db-new
mv local_data/geocode.db{-new,}
appcfg.py download_data --application=dancedeets --kind="LocationMapping" --url=http://dancedeets.appspot.com/_ah/remote_api --filename=local_data/locationmapping.db-new
mv local_data/locationmapping.db{-new,}
appcfg.py download_data --application=dancedeets --kind="Source" --url=http://dancedeets.appspot.com/_ah/remote_api --filename=local_data/source.db-new
mv local_data/source.db{-new,}

#appcfg.py upload_data --application=dancedeets --kind="DBEvent" --url=http://127.0.0.1:8080/_ah/remote_api --filename=events.db
#appcfg.py upload_data --application=dancedeets --kind="PotentialEvent" --url=http://127.0.0.1:8080/_ah/remote_api --filename=potentialevents.db
#appcfg.py upload_data --application=dancedeets --kind="FacebookCachedObject" --url=http://127.0.0.1:8080/_ah/remote_api --filename=fb_data.db
#appcfg.py upload_data --application=dancedeets --kind="City" --url=http://127.0.0.1:8080/_ah/remote_api --filename=city.db
#appcfg.py upload_data --application=dancedeets --kind="GeoCode" --url=http://127.0.0.1:8080/_ah/remote_api --filename=city.db
#appcfg.py upload_data --application=dancedeets --kind="LocationMapping" --url=http://127.0.0.1:8080/_ah/remote_api --filename=city.db
#appcfg.py upload_data --application=dancedeets --kind="Source" --url=http://127.0.0.1:8080/_ah/remote_api --filename=city.db
rm bulkloader-*
