import scrapy
from scrapy import item

from scrapy_lib import pipelines

class SaveFacebookEventPipeline(pipelines.SaveEventsToServerPipeline):
    server_path = 'web_events/upload_multi_fbevent'
    batch_size = 20


class FbEventScraper(scrapy.Spider):
    """Base class for all our fb event scrapers. Does some per-item field setup that is common across web events."""

    custom_settings = {
        'ITEM_PIPELINES': {
            'web_events.scraper.fbitems.SaveFacebookEventPipeline': 300,
        }
    }

    @staticmethod
    def add_url(url):
        return {'url': url}
