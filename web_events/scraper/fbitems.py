import scrapy
from scrapy import item

from scrapy_lib import pipelines

class AddFacebookEvent(item.DictItem):
    fields = ['url']

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.__dict__)


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
