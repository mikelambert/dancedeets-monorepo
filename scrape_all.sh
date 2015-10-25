cat classes/scrapy/spiders/*.py | grep '^\sname = ' | grep -o "'.*'" | xargs -I{} ./scrapy.py crawl {}
curl http://www.dancedeets.com/classes/reindex
curl http://dev.dancedeets.com:8080/classes/reindex

