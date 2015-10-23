cat classes/scrapy/spiders/*.py | grep '^\sname = ' | grep -o "'.*'" | xargs -I{} ./scrapy.py crawl {}
