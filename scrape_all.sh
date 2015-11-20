path=$(dirname $0)
cat $path/classes/scrapy/spiders/*.py | grep '^\sname = ' | grep -o "'.*'" | xargs -I{} $path/scrapy.sh crawl {}
curl http://www.dancedeets.com/classes/reindex
curl http://dev.dancedeets.com:8080/classes/reindex

