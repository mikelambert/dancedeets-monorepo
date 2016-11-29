path=$(dirname $0)
cat $path/web_events/scraper/spiders/*.py | grep '^\s*name = ' | grep -o "'.*'" | xargs -I{} $path/scrapy.sh crawl {}
