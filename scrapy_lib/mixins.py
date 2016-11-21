import keys


SERVER_URL = 'https://b54f18og-splash.scrapinghub.com'

# Or...to test this code locally, you must run a Splash server.
# Start a docker server running splash, as described here:
# http://splash.readthedocs.org/en/latest/install.html
# For Mac OS X, I ran Docker Quickstart Terminal, and then ran the command from the docs:
# $ docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 scrapinghub/splash
# Then configure the SERVER_URL to point at your local instance,
# in my case: 192.168.99.100
# SERVER_URL = 'http://192.168.99.100:8050'

class BrowserScraperMixin(object):
    # So we can log in to our scrapinghub splash instance
    http_user = keys.get('scrapinghub_key')
    http_pass = ''



def generate_custom_settings(kwargs):
    custom_settings = {
        'SPLASH_URL': SERVER_URL,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapyjs.SplashMiddleware': 725,
            'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 800,
        },
        'DUPEFILTER_CLASS': 'scrapyjs.SplashAwareDupeFilter',
        'HTTPCACHE_STORAGE': 'scrapyjs.SplashAwareFSCacheStorage',
    }
    custom_settings.update(kwargs)
    return custom_settings
